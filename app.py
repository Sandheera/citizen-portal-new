import os
import json
from flask import Flask, jsonify, render_template, request, session, redirect, send_file, abort
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from io import StringIO
import csv
from dotenv import load_dotenv
import bcrypt
import pathlib

# AI / embeddings (lazy import)
import numpy as np

# faiss may not be present on every host — allow fallback
try:
    import faiss
    FAISS_AVAILABLE = True
except Exception:
    FAISS_AVAILABLE = False

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")
CORS(app)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
    # Test connection
    client.admin.command('ping')
    print("✓ MongoDB connected")
except Exception as e:
    print(f"⚠ MongoDB connection failed: {e}")
    print("  App will start but database operations will fail.")
    client = None

if client:
    db = client["citizen_portal"]
    services_col = db["services"]       # original services (ministries + subservices)
    subservices_col = db["subservices"] # new: optional separate collection
    admins_col = db["admins"]
    eng_col = db["engagements"]
    categories_col = db["categories"]   # new: category groups
    officers_col = db["officers"]       # new: officers metadata
    ads_col = db["ads"]                 # new: ads & training program announcements
    users_col = db["users"]             # new: progressive profile / accounts
else:
    db = None
    services_col = None
    subservices_col = None
    admins_col = None
    eng_col = None
    categories_col = None
    officers_col = None
    ads_col = None
    users_col = None

# Embedding model (lazy-init)
EMBED_MODEL = None

INDEX_PATH = pathlib.Path("./data/faiss.index")
META_PATH = pathlib.Path("./data/faiss_meta.json")
VECTOR_DIM = 384  # for all-MiniLM-L6-v2

def get_embedding_model():
    global EMBED_MODEL
    if EMBED_MODEL is None:
        from sentence_transformers import SentenceTransformer
        EMBED_MODEL = SentenceTransformer(os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
    return EMBED_MODEL

# --- Helpers ---
def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*a, **kw):
        if not session.get("admin_logged_in"):
            return jsonify({"error":"unauthorized"}), 401
        return fn(*a, **kw)
    return wrapper

# --- Public pages ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
def admin_page():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")
    return render_template("admin.html")

@app.route("/admin/manage")
@admin_required
def manage_page():
    return render_template("manage.html")

# --- API: services & categories (public) ---
@app.route("/api/services")
def get_services():
    docs = list(services_col.find({}, {"_id":0}))
    return jsonify(docs)

@app.route("/api/categories")
def get_categories():
    # categories collection contains category documents: {id, name:{en,si,ta}, ministries:[id,...]}
    cats = list(categories_col.find({}, {"_id":0}))
    
    # if not seeded, create dynamic categories from existing services grouped by service.category
    if not cats:
        pipeline = [
            {"$project":{"id":1,"name":1,"category":1,"subservices":1}},
            {"$group":{"_id":"$category","ministries":{"$push":{"id":"$id","name":"$name"}}}}
        ]
        try:
            groups = list(services_col.aggregate(pipeline))
            cats = [{"id":g["_id"] or "uncategorized","name":{"en":g["_id"] or "Uncategorized"},"ministries":g["ministries"]} for g in groups]
        except Exception:
            cats = []
    
    return jsonify(cats)

@app.route("/api/service/<service_id>")
def get_service(service_id):
    doc = services_col.find_one({"id": service_id}, {"_id":0})
    return jsonify(doc or {})

# Autosuggest search (quick matches for typeahead)
@app.route("/api/search/autosuggest")
def autosuggest():
    q = request.args.get("q","").strip()
    if not q:
        return jsonify([])
    
    # simple text search across service names and subservice names
    regex = {"$regex": q, "$options": "i"}
    results = []
    for s in services_col.find({"$or":[{"name.en":regex},{"subservices.name.en":regex}]}, {"_id":0, "id":1, "name":1, "subservices":1}).limit(20):
        results.append(s)
    return jsonify(results)

# Engagement logging (unchanged but extended to include ad clicks / profile step)
@app.route("/api/engagement", methods=["POST"])
def log_engagement():
    payload = request.json or {}
    doc = {
        "user_id": payload.get("user_id") or None,
        "age": int(payload.get("age")) if payload.get("age") else None,
        "job": payload.get("job"),
        "desires": payload.get("desires") or [],
        "question_clicked": payload.get("question_clicked"),
        "service": payload.get("service"),
        "ad": payload.get("ad"),
        "source": payload.get("source"),
        "timestamp": datetime.utcnow()
    }
    eng_col.insert_one(doc)
    return jsonify({"status":"ok"})

# Progressive profile: save step-by-step partial profile (upsert by anonymous id or email)
@app.route("/api/profile/step", methods=["POST"])
def profile_step():
    payload = request.json or {}
    profile_id = payload.get("profile_id") or None
    email = payload.get("email")
    data = payload.get("data",{})
    
    if profile_id:
        users_col.update_one({"_id": ObjectId(profile_id)}, {"$set": {"profile."+payload.get("step", "unknown"): data, "updated": datetime.utcnow()}}, upsert=True)
        return jsonify({"status":"ok", "profile_id":profile_id})
    
    if email:
        res = users_col.find_one_and_update({"email":email}, {"$set": {"profile."+payload.get("step","unknown"): data, "updated": datetime.utcnow()}}, upsert=True, return_document=True)
        return jsonify({"status":"ok", "profile_id": str(res.get("_id"))})
    
    # fallback - create anonymous
    new_id = users_col.insert_one({"profile": {payload.get("step","unknown"):data}, "created":datetime.utcnow()}).inserted_id
    return jsonify({"status":"ok", "profile_id": str(new_id)})

# Ads
@app.route("/api/ads")
def get_ads():
    ads = list(ads_col.find({}, {"_id":0}))
    return jsonify(ads)

# --- AI / vector index endpoints ---
def build_vector_index():
    """
    Build or rebuild a FAISS index from services_col. Saves index file + metadata.
    This should be run via /api/admin/build_index by admin after seeding/updating services.
    """
    os.makedirs("data", exist_ok=True)
    docs = []
    
    # flatten each service/subservice/question to a searchable doc
    for svc in services_col.find():
        svc_id = svc.get("id")
        svc_name = svc.get("name", {}).get("en") or svc.get("name")
        for sub in svc.get("subservices", []):
            sub_id = sub.get("id")
            sub_name = sub.get("name", {}).get("en") or sub.get("name")
            # base content: service+subservice name + question text + answer
            for q in sub.get("questions", []):
                q_text = q.get("q", {}).get("en") or q.get("q")
                a_text = q.get("answer", {}).get("en") or q.get("answer")
                content = " | ".join([svc_name or "", sub_name or "", q_text or "", a_text or ""])
                docs.append({
                    "doc_id": f"{svc_id}::{sub_id}::{q_text[:80]}",
                    "service_id": svc_id,
                    "subservice_id": sub_id,
                    "title": q_text,
                    "content": content,
                    "metadata": {
                        "downloads": q.get("downloads", []),
                        "location": q.get("location"),
                        "instructions": q.get("instructions")
                    }
                })
    
    # embed
    model = get_embedding_model()
    texts = [d["content"] for d in docs]
    if not texts:
        # nothing to index
        return {"count":0}
    
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    
    # normalize for cosine if using IP
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms==0] = 1.0
    embeddings = embeddings / norms
    
    if FAISS_AVAILABLE:
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        # store id mapping separately
        index.add(embeddings.astype(np.float32))
        faiss.write_index(index, str(INDEX_PATH))
    else:
        # fallback: store embeddings in JSON (slow search)
        np.save("data/embeddings.npy", embeddings)
    
    # save metadata
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    
    return {"count": len(docs), "faiss": FAISS_AVAILABLE}

@app.route("/api/admin/build_index", methods=["POST"])
@admin_required
def admin_build_index():
    res = build_vector_index()
    return jsonify(res)

def search_vectors(query, top_k=5):
    model = get_embedding_model()
    q_emb = model.encode([query], convert_to_numpy=True)
    q_emb = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-10)
    
    if FAISS_AVAILABLE and INDEX_PATH.exists() and META_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))
        D, I = index.search(q_emb.astype(np.float32), top_k)
        with open(META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
        hits = []
        for idx in I[0]:
            if idx < len(meta):
                hits.append(meta[idx])
        return hits
    else:
        # fallback linear scan
        if not META_PATH.exists():
            return []
        meta = json.load(open(META_PATH, "r", encoding="utf-8"))
        if not os.path.exists("data/embeddings.npy"):
            return []
        db_emb = np.load("data/embeddings.npy")
        sims = (db_emb @ q_emb[0]).tolist()
        idxs = np.argsort(sims)[::-1][:top_k]
        return [meta[int(i)] for i in idxs]

@app.route("/api/ai/search", methods=["POST"])
def ai_search():
    """
    Accepts: {query: "...", top_k: 5}
    Returns: {answer: "...", sources: [ {...} ] }
    """
    payload = request.json or {}
    query = payload.get("query","").strip()
    top_k = int(payload.get("top_k", 5))
    
    if not query:
        return jsonify({"error":"empty query"}), 400
    
    hits = search_vectors(query, top_k)
    
    # Build a simple answer: concatenate top answers and include source pointers
    # Optionally: here you would call an LLM (OpenAI) to produce a natural language answer
    answer_parts = []
    sources = []
    
    for h in hits:
        # safe fallback: use "title" + "content" truncated
        txt = h.get("content","")
        answer_parts.append(txt[:800])
        sources.append({"service_id": h.get("service_id"), "subservice_id": h.get("subservice_id"), "title": h.get("title"), **h.get("metadata",{})})
    
    answer = "\n\n---\n\n".join(answer_parts) if answer_parts else "No matching content found."
    
    return jsonify({"query": query, "answer": answer, "sources": sources, "hits": len(sources)})

# --- Admin auth with bcrypt ---
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin.html")
    
    data = request.form
    username = data.get("username")
    password = data.get("password", "")
    admin = admins_col.find_one({"username": username})
    
    if admin:
        stored = admin.get("password")
        try:
            ok = bcrypt.checkpw(password.encode("utf-8"), stored)
        except Exception:
            ok = stored == password  # legacy plain password fallback
        
        if ok:
            session["admin_logged_in"] = True
            session["admin_user"] = username
            return redirect("/admin")
    
    return "Login failed", 401

@app.route("/api/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    session.clear()
    return jsonify({"status":"logged out"})

# --- Admin CRUD: services (unchanged), categories, officers, ads ---
@app.route("/api/admin/services", methods=["GET","POST"])
@admin_required
def admin_services():
    if request.method == "GET":
        return jsonify(list(services_col.find({}, {"_id":0})))
    
    payload = request.json
    sid = payload.get("id")
    if not sid:
        return jsonify({"error":"id required"}), 400
    
    services_col.update_one({"id": sid}, {"$set": payload}, upsert=True)
    return jsonify({"status":"ok"})

@app.route("/api/admin/services/<service_id>", methods=["DELETE"])
@admin_required
def delete_service(service_id):
    services_col.delete_one({"id": service_id})
    return jsonify({"status":"deleted"})

# categories
@app.route("/api/admin/categories", methods=["GET","POST","DELETE"])
@admin_required
def manage_categories():
    if request.method == "GET":
        return jsonify(list(categories_col.find({}, {"_id":0})))
    
    if request.method == "POST":
        payload = request.json
        cid = payload.get("id")
        if not cid: return jsonify({"error":"id required"}), 400
        
        # ensure subcategories array exists
        if "subcategories" not in payload:
            payload["subcategories"] = []
        
        categories_col.update_one({"id":cid}, {"$set":payload}, upsert=True)
        return jsonify({"status":"ok"})
    
    if request.method == "DELETE":
        cid = request.args.get("id")
        categories_col.delete_one({"id":cid})
        return jsonify({"status":"deleted"})

# Add subcategory to existing category
@app.route("/api/admin/categories/add-subcategory", methods=["POST"])
@admin_required
def add_subcategory():
    payload = request.json
    parent_id = payload.get("parentId")
    subcategory = payload.get("subcategory")
    
    if not parent_id or not subcategory:
        return jsonify({"error":"parentId and subcategory required"}), 400
    
    categories_col.update_one(
        {"id": parent_id},
        {"$push": {"subcategories": subcategory}}
    )
    return jsonify({"status":"ok"})

# officers
@app.route("/api/admin/officers", methods=["GET","POST","DELETE"])
@admin_required
def manage_officers():
    if request.method == "GET":
        return jsonify(list(officers_col.find({}, {"_id":0})))
    
    if request.method == "POST":
        payload = request.json
        oid = payload.get("id")
        if not oid: return jsonify({"error":"id required"}), 400
        officers_col.update_one({"id":oid}, {"$set":payload}, upsert=True)
        return jsonify({"status":"ok"})
    
    if request.method == "DELETE":
        oid = request.args.get("id")
        officers_col.delete_one({"id":oid})
        return jsonify({"status":"deleted"})

# ads
@app.route("/api/admin/ads", methods=["GET","POST","DELETE"])
@admin_required
def manage_ads():
    if request.method == "GET":
        return jsonify(list(ads_col.find({}, {"_id":0})))
    
    if request.method == "POST":
        payload = request.json
        aid = payload.get("id")
        if not aid: return jsonify({"error":"id required"}), 400
        ads_col.update_one({"id":aid}, {"$set":payload}, upsert=True)
        return jsonify({"status":"ok"})
    
    if request.method == "DELETE":
        aid = request.args.get("id")
        ads_col.delete_one({"id":aid})
        return jsonify({"status":"deleted"})

# --- Admin insights (kept but extended) ---
@app.route("/api/admin/insights")
@admin_required
def admin_insights():
    # Age groups, jobs, services, questions (as before) ... plus top ads (clicks)
    age_groups = {"<18":0,"18-25":0,"26-40":0,"41-60":0,"60+":0}
    for e in eng_col.find({}, {"age":1}):
        age = e.get("age")
        if not age:
            continue
        try:
            age = int(age)
            if age < 18: age_groups["<18"] += 1
            elif age <= 25: age_groups["18-25"] += 1
            elif age <= 40: age_groups["26-40"] += 1
            elif age <= 60: age_groups["41-60"] += 1
            else: age_groups["60+"] += 1
        except:
            continue
    
    jobs = {}
    services = {}
    questions = {}
    desires = {}
    
    for e in eng_col.find({}, {"job":1,"service":1,"question_clicked":1,"desires":1,"ad":1}):
        j = (e.get("job") or "Unknown").strip()
        jobs[j] = jobs.get(j,0) + 1
        s = e.get("service") or "Unknown"
        services[s] = services.get(s,0) + 1
        q = e.get("question_clicked") or "Unknown"
        questions[q] = questions.get(q,0) + 1
        for d in e.get("desires") or []:
            desires[d] = desires.get(d,0) + 1
    
    # premium suggestions
    pipeline = [
        {"$group": {"_id": {"user":"$user_id","question":"$question_clicked"}, "count":{"$sum":1}}},
        {"$match": {"count": {"$gte": 2}}}
    ]
    repeated = list(eng_col.aggregate(pipeline))
    premium_suggestions = [{"user": r["_id"]["user"], "question": r["_id"]["question"], "count": r["count"]} for r in repeated if r["_id"]["user"]]
    
    return jsonify({
        "age_groups": age_groups,
        "jobs": jobs,
        "services": services,
        "questions": questions,
        "desires": desires,
        "premium_suggestions": premium_suggestions
    })

@app.route("/api/admin/engagements")
@admin_required
def admin_engagements():
    items = []
    for e in eng_col.find().sort("timestamp",-1).limit(500):
        e["_id"] = str(e["_id"])
        e["timestamp"] = e.get("timestamp").isoformat()
        items.append(e)
    return jsonify(items)

# CSV export (unchanged)
@app.route("/api/admin/export_csv")
@admin_required
def export_csv():
    cursor = eng_col.find()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["user_id","age","job","desire","question","service","ad","timestamp"])
    for e in cursor:
        cw.writerow([
            e.get("user_id"), e.get("age"), e.get("job"),
            ",".join(e.get("desires") or []),
            e.get("question_clicked"), e.get("service"), e.get("ad"),
            e.get("timestamp").isoformat() if e.get("timestamp") else ""
        ])
    si.seek(0)
    return send_file(
        StringIO(si.read()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="engagements.csv"
    )

# --- Subcategory Items & Applications ---
@app.route("/api/subcategory/<subcategory_id>/items")
def get_subcategory_items(subcategory_id):
    """Get all service items within a subcategory"""
    category = categories_col.find_one({"subcategories.id": subcategory_id}, {"_id": 0})
    if not category:
        return jsonify([])
    subcategory = next((sub for sub in category.get("subcategories", []) if sub["id"] == subcategory_id), None)
    if not subcategory:
        return jsonify([])
    return jsonify(subcategory.get("items", []))

@app.route("/api/subcategory/<subcategory_id>/items/<item_id>")
def get_item_details(subcategory_id, item_id):
    """Get specific item details"""
    category = categories_col.find_one({"subcategories.id": subcategory_id}, {"_id": 0})
    if not category:
        return jsonify({"error": "Not found"}), 404
    subcategory = next((sub for sub in category.get("subcategories", []) if sub["id"] == subcategory_id), None)
    if not subcategory:
        return jsonify({"error": "Subcategory not found"}), 404
    item = next((itm for itm in subcategory.get("items", []) if itm.get("id") == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)

@app.route("/api/subcategory/<subcategory_id>/items/<item_id>/apply", methods=["POST"])
def submit_application(subcategory_id, item_id):
    """Submit application for a service"""
    payload = request.json or {}
    application = {
        "subcategory_id": subcategory_id,
        "item_id": item_id,
        "user_id": payload.get("user_id"),
        "application_data": payload.get("data", {}),
        "status": "pending",
        "submitted_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = db["applications"].insert_one(application)
    eng_col.insert_one({
        "user_id": payload.get("user_id"),
        "subcategory_id": subcategory_id,
        "item_id": item_id,
        "action": "application_submitted",
        "timestamp": datetime.utcnow()
    })
    return jsonify({
        "status": "success",
        "application_id": str(result.inserted_id),
        "message": "Application submitted successfully"
    })

@app.route("/api/admin/subcategory/<subcategory_id>/applications")
@admin_required
def get_applications(subcategory_id):
    """Get all applications for a subcategory"""
    applications = list(db["applications"].find({"subcategory_id": subcategory_id}).sort("submitted_at", -1).limit(100))
    for app in applications:
        app["_id"] = str(app["_id"])
        if app.get("submitted_at"):
            app["submitted_at"] = app["submitted_at"].isoformat()
        if app.get("updated_at"):
            app["updated_at"] = app["updated_at"].isoformat()
    return jsonify(applications)

@app.route("/api/admin/applications/<application_id>/status", methods=["POST"])
@admin_required
def update_app_status(application_id):
    """Update application status"""
    payload = request.json or {}
    new_status = payload.get("status")
    if new_status not in ["pending", "approved", "rejected", "processing"]:
        return jsonify({"error": "Invalid status"}), 400
    db["applications"].update_one(
        {"_id": ObjectId(application_id)},
        {"$set": {"status": new_status, "updated_at": datetime.utcnow(), "admin_notes": payload.get("notes", "")}}
    )
    return jsonify({"status": "Application updated"})

@app.route("/api/admin/subcategory/<subcategory_id>/report")
@admin_required
def subcategory_report(subcategory_id):
    """Detailed report for single subcategory"""
    all_categories = list(categories_col.find({}, {"_id":0}))
    parent_cat = None
    sub_details = None
    for cat in all_categories:
        for sub in cat.get("subcategories", []):
            if sub.get("id") == subcategory_id:
                parent_cat = cat
                sub_details = sub
                break
        if sub_details:
            break
    if not sub_details:
        return jsonify({"error": "Subcategory not found"}), 404
    engagements = list(eng_col.find({"subcategory_id": subcategory_id}))
    total_views = len(engagements)
    unique_users = len(set(e.get("user_id") for e in engagements if e.get("user_id")))
    age_distribution = {"<18": 0, "18-25": 0, "26-40": 0, "41-60": 0, "60+": 0}
    for e in engagements:
        age = e.get("age")
        if age:
            try:
                age = int(age)
                if age < 18: age_distribution["<18"] += 1
                elif age <= 25: age_distribution["18-25"] += 1
                elif age <= 40: age_distribution["26-40"] += 1
                elif age <= 60: age_distribution["41-60"] += 1
                else: age_distribution["60+"] += 1
            except:
                pass
    job_distribution = {}
    for e in engagements:
        job = e.get("job")
        if job:
            job_distribution[job] = job_distribution.get(job, 0) + 1
    report = {
        "subcategory": {
            "id": subcategory_id,
            "name": sub_details.get("name", {}),
            "description": sub_details.get("description", ""),
            "keywords": sub_details.get("keywords", []),
            "itemCount": sub_details.get("itemCount", 0)
        },
        "parent_category": {
            "id": parent_cat.get("id") if parent_cat else None,
            "name": parent_cat.get("name", {}) if parent_cat else {},
            "icon": parent_cat.get("icon", "📁") if parent_cat else "📁",
            "color": parent_cat.get("color", "#0b3b8c") if parent_cat else "#0b3b8c"
        },
        "metrics": {
            "total_views": total_views,
            "unique_users": unique_users,
            "avg_views_per_user": round(total_views / unique_users, 2) if unique_users > 0 else 0
        },
        "demographics": {
            "age_distribution": age_distribution,
            "job_distribution": sorted(job_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    }
    return jsonify(report)

# ==================== CRUD FOR SERVICE ITEMS ====================

@app.route("/api/admin/items", methods=["GET"])
@admin_required
def get_all_items():
    """Get all service items across all categories"""
    all_items = []
    for cat in categories_col.find({}, {"_id": 0}):
        for sub in cat.get("subcategories", []):
            for item in sub.get("items", []):
                all_items.append({
                    **item,
                    "category_id": cat["id"],
                    "category_name": cat["name"]["en"],
                    "subcategory_id": sub["id"],
                    "subcategory_name": sub["name"]["en"]
                })
    return jsonify(all_items)

@app.route("/api/admin/subcategory/<subcategory_id>/items", methods=["POST"])
@admin_required  
def add_service_item(subcategory_id):
    """Add new service item to subcategory"""
    payload = request.json or {}
    category = categories_col.find_one({"subcategories.id": subcategory_id}, {"_id": 0, "id": 1})
    if not category:
        return jsonify({"error": "Subcategory not found"}), 404
    new_item = {
        "id": payload.get("id"),
        "title": payload.get("title"),
        "description": payload.get("description"),
        "requirements": payload.get("requirements", []),
        "fee": payload.get("fee"),
        "processingTime": payload.get("processingTime"),
        "formFields": payload.get("formFields", []),
        "status": payload.get("status", "active")
    }
    categories_col.update_one(
        {"id": category["id"], "subcategories.id": subcategory_id},
        {"$push": {"subcategories.$.items": new_item}, "$inc": {"subcategories.$.itemCount": 1}}
    )
    return jsonify({"status": "Item added", "item": new_item})

@app.route("/api/admin/subcategory/<subcategory_id>/items/<item_id>", methods=["PUT"])
@admin_required
def update_service_item(subcategory_id, item_id):
    """Update existing service item"""
    payload = request.json or {}
    category = categories_col.find_one({"subcategories.id": subcategory_id}, {"_id": 0, "id": 1, "subcategories": 1})
    if not category:
        return jsonify({"error": "Not found"}), 404
    subcategory = next((s for s in category.get("subcategories", []) if s["id"] == subcategory_id), None)
    if not subcategory:
        return jsonify({"error": "Subcategory not found"}), 404
    items = subcategory.get("items", [])
    for i, item in enumerate(items):
        if item.get("id") == item_id:
            items[i] = {**item, **payload}
            break
    categories_col.update_one(
        {"id": category["id"], "subcategories.id": subcategory_id},
        {"$set": {"subcategories.$.items": items}}
    )
    return jsonify({"status": "Item updated"})

@app.route("/api/admin/subcategory/<subcategory_id>/items/<item_id>", methods=["DELETE"])
@admin_required
def delete_service_item(subcategory_id, item_id):
    """Delete service item"""
    category = categories_col.find_one({"subcategories.id": subcategory_id}, {"_id": 0, "id": 1})
    if not category:
        return jsonify({"error": "Not found"}), 404
    categories_col.update_one(
        {"id": category["id"], "subcategories.id": subcategory_id},
        {"$pull": {"subcategories.$.items": {"id": item_id}}, "$inc": {"subcategories.$.itemCount": -1}}
    )
    return jsonify({"status": "Item deleted"})

# ==================== ADMIN APPLICATION MANAGEMENT ====================

@app.route("/api/admin/applications/all")
@admin_required
def get_all_applications_admin():
    """Get all applications for admin review"""
    applications = list(db["applications"].find().sort("submitted_at", -1).limit(100))
    for app in applications:
        app["_id"] = str(app["_id"])
        if app.get("submitted_at"):
            app["submitted_at"] = app["submitted_at"].isoformat()
        if app.get("updated_at"):
            app["updated_at"] = app["updated_at"].isoformat()
    return jsonify(applications)

@app.route("/api/admin/applications/<application_id>/approve", methods=["POST"])
@admin_required
def approve_application(application_id):
    """Approve an application"""
    payload = request.json or {}
    db["applications"].update_one(
        {"_id": ObjectId(application_id)},
        {"$set": {
            "status": "approved",
            "updated_at": datetime.utcnow(),
            "admin_notes": payload.get("notes", "Application approved"),
            "approved_by": session.get("admin_username", "admin")
        }}
    )
    return jsonify({"status": "Application approved"})

@app.route("/api/admin/applications/<application_id>/reject", methods=["POST"])
@admin_required
def reject_application(application_id):
    """Reject an application"""
    payload = request.json or {}
    db["applications"].update_one(
        {"_id": ObjectId(application_id)},
        {"$set": {
            "status": "rejected",
            "updated_at": datetime.utcnow(),
            "admin_notes": payload.get("notes", "Application rejected"),
            "rejected_by": session.get("admin_username", "admin")
        }}
    )
    return jsonify({"status": "Application rejected"})

@app.route("/api/admin/applications/<application_id>/update", methods=["PUT"])
@admin_required
def update_application_admin(application_id):
    """Update application details"""
    payload = request.json or {}
    update_data = {
        "updated_at": datetime.utcnow(),
        "updated_by": session.get("admin_username", "admin")
    }
    if "application_data" in payload:
        update_data["application_data"] = payload["application_data"]
    if "admin_notes" in payload:
        update_data["admin_notes"] = payload["admin_notes"]
    if "status" in payload:
        update_data["status"] = payload["status"]
    
    db["applications"].update_one(
        {"_id": ObjectId(application_id)},
        {"$set": update_data}
    )
    return jsonify({"status": "Application updated"})

@app.route("/api/admin/reports/applications-pdf")
@admin_required
def generate_applications_pdf():
    """Generate PDF report of all applications"""
    applications = list(db["applications"].find().sort("submitted_at", -1))
    
    # Count by status
    stats = {
        "total": len(applications),
        "pending": len([a for a in applications if a.get("status") == "pending"]),
        "approved": len([a for a in applications if a.get("status") == "approved"]),
        "rejected": len([a for a in applications if a.get("status") == "rejected"]),
        "processing": len([a for a in applications if a.get("status") == "processing"])
    }
    
    html_content = f"""
    <html>
    <head>
        <title>Applications Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            h1 {{ color: #0b3b8c; border-bottom: 3px solid #0b3b8c; padding-bottom: 10px; }}
            .summary {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin: 20px 0; }}
            .summary-card {{ background: #f5f5f5; padding: 15px; border-radius: 8px; text-align: center; }}
            .summary-card .label {{ font-size: 12px; color: #666; }}
            .summary-card .value {{ font-size: 24px; font-weight: bold; color: #0b3b8c; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 12px; }}
            th {{ background: #0b3b8c; color: white; }}
            tr:nth-child(even) {{ background: #f9f9f9; }}
            .status-pending {{ color: #f57c00; font-weight: bold; }}
            .status-approved {{ color: #388e3c; font-weight: bold; }}
            .status-rejected {{ color: #d32f2f; font-weight: bold; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 11px; color: #999; }}
        </style>
    </head>
    <body>
        <h1>📊 Applications Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <div class="summary-card">
                <div class="label">Total</div>
                <div class="value">{stats['total']}</div>
            </div>
            <div class="summary-card">
                <div class="label">Pending</div>
                <div class="value">{stats['pending']}</div>
            </div>
            <div class="summary-card">
                <div class="label">Approved</div>
                <div class="value">{stats['approved']}</div>
            </div>
            <div class="summary-card">
                <div class="label">Rejected</div>
                <div class="value">{stats['rejected']}</div>
            </div>
            <div class="summary-card">
                <div class="label">Processing</div>
                <div class="value">{stats['processing']}</div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Application ID</th>
                    <th>User ID</th>
                    <th>Subcategory</th>
                    <th>Item</th>
                    <th>Status</th>
                    <th>Submitted</th>
                </tr>
            </thead>
            <tbody>
                {"".join([f'''
                <tr>
                    <td>{str(app['_id'])[-8:].upper()}</td>
                    <td>{app.get('user_id', 'N/A')[:20]}</td>
                    <td>{app.get('subcategory_id', 'N/A')}</td>
                    <td>{app.get('item_id', 'N/A')}</td>
                    <td class="status-{app.get('status', 'pending')}">{app.get('status', 'pending').upper()}</td>
                    <td>{app.get('submitted_at', 'N/A')}</td>
                </tr>
                ''' for app in applications[:50]])}
            </tbody>
        </table>
        
        <div class="footer">
            <p>Citizen Services Portal - Administrative Report</p>
            <p>This report is confidential and for internal use only</p>
        </div>
    </body>
    </html>
    """
    
    return html_content

# ==================== USER APPLICATION TRACKING ====================

@app.route("/api/my-applications/<user_id>")
def get_user_applications(user_id):
    """Get all applications submitted by a user"""
    applications = list(db["applications"].find({"user_id": user_id}).sort("submitted_at", -1))
    for app in applications:
        app["_id"] = str(app["_id"])
        if app.get("submitted_at"):
            app["submitted_at"] = app["submitted_at"].isoformat()
        if app.get("updated_at"):
            app["updated_at"] = app["updated_at"].isoformat()
    return jsonify(applications)

@app.route("/api/my-applications/<user_id>/<application_id>", methods=["DELETE"])
def cancel_user_application(user_id, application_id):
    """Cancel a pending application"""
    result = db["applications"].update_one(
        {"_id": ObjectId(application_id), "user_id": user_id, "status": "pending"},
        {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
    )
    if result.modified_count > 0:
        return jsonify({"status": "Application cancelled"})
    else:
        return jsonify({"error": "Cannot cancel this application"}), 400

@app.route("/api/application-stats/<user_id>")
def get_user_application_stats(user_id):
    """Get statistics about user's applications"""
    pipeline = [{"$match": {"user_id": user_id}}, {"$group": {"_id": "$status", "count": {"$sum": 1}}}]
    stats_list = list(db["applications"].aggregate(pipeline))
    stats = {item["_id"]: item["count"] for item in stats_list}
    return jsonify({
        "total": sum(stats.values()),
        "pending": stats.get("pending", 0),
        "approved": stats.get("approved", 0),
        "rejected": stats.get("rejected", 0),
        "processing": stats.get("processing", 0),
        "cancelled": stats.get("cancelled", 0)
    })

@app.route("/api/my-applications/<user_id>/<application_id>/update-status", methods=["POST"])
def update_user_application_status(user_id, application_id):
    """Update application status (public endpoint for users to manage their own applications)"""
    payload = request.json or {}
    new_status = payload.get("status")
    notes = payload.get("notes", "")
    
    if new_status not in ["pending", "approved", "rejected", "processing", "cancelled"]:
        return jsonify({"error": "Invalid status"}), 400
    
    # Update application
    result = db["applications"].update_one(
        {"_id": ObjectId(application_id), "user_id": user_id},
        {"$set": {
            "status": new_status,
            "updated_at": datetime.utcnow(),
            "admin_notes": notes if notes else ""
        }}
    )
    
    if result.modified_count > 0:
        return jsonify({"status": "success", "message": "Application updated"})
    else:
        return jsonify({"error": "Application not found or no changes made"}), 404

# ensure at least one admin user exists (hashed)
if __name__ == "__main__":
    if admins_col is not None and admins_col.count_documents({}) == 0:
        pwd = os.getenv("ADMIN_PWD","admin123")
        hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
        admins_col.insert_one({"username":"admin","password": hashed})
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT",5000)))