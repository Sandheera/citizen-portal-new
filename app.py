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
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-change-in-production")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
CORS(app, supports_credentials=True)

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
    services_col = db["services"]
    subservices_col = db["subservices"]
    admins_col = db["admins"]
    eng_col = db["engagements"]
    categories_col = db["categories"]
    officers_col = db["officers"]
    ads_col = db["ads"]
    users_col = db["users"]
    # NEW COLLECTIONS
    shop_products_col = db["shop_products"]
    shop_orders_col = db["shop_orders"]
    shop_cart_col = db["shop_carts"]
    shop_ratings_col = db["shop_ratings"]
    user_profiles_col = db["user_profiles"]     # extended profiles
    behavior_col = db["behavior_events"]        # click/search/time tracking
    consent_col = db["user_consents"]           # GDPR consent records
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
    shop_products_col = None
    shop_orders_col = None
    shop_cart_col = None
    shop_ratings_col = None
    user_profiles_col = None
    behavior_col = None
    consent_col = None

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
@app.route("/portal")
def portal_home():
    return render_template("index.html")

@app.route("/")
def home():
    if not session.get("admin_logged_in"):
        return redirect("/login")
    return redirect("/dashboard")

@app.route("/admin")
def admin_page():
    if not session.get("admin_logged_in"):
        return redirect("/login")
    return redirect("/dashboard")

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
@app.route("/login", methods=["GET", "POST"])
def login_page():
    # GET → show the login page
    if request.method == "GET":
        try:
            if session.get("admin_logged_in"):
                return redirect("/dashboard")
            return render_template("login.html")
        except Exception as e:
            # If template missing, return inline HTML
            return """<!DOCTYPE html><html><head><title>Login</title></head><body style="font-family:sans-serif;background:#070b14;color:white;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
            <div style="background:#111827;padding:40px;border-radius:16px;width:340px;text-align:center">
            <h2 style="margin-bottom:24px">Admin Login</h2>
            <p style="color:#f43f5e;font-size:13px;margin-bottom:16px">Template error: """ + str(e) + """<br>Copy login.html to templates/</p>
            <form method="post" action="/login-form">
            <input name="username" placeholder="Username" style="width:100%;padding:11px;margin-bottom:12px;border-radius:8px;border:1px solid #333;background:#1a2235;color:white;font-size:14px;box-sizing:border-box"><br>
            <input name="password" type="password" placeholder="Password" style="width:100%;padding:11px;margin-bottom:16px;border-radius:8px;border:1px solid #333;background:#1a2235;color:white;font-size:14px;box-sizing:border-box"><br>
            <button type="submit" style="width:100%;padding:13px;background:#2563eb;color:white;border:none;border-radius:8px;font-size:15px;font-weight:700;cursor:pointer">Sign In</button>
            </form></div></body></html>""", 200

    # POST via JSON (from login.html fetch)
    try:
        body = request.get_json(force=True, silent=True) or {}
        username = str(body.get("username", "")).strip()
        password = str(body.get("password", ""))
    except Exception as e:
        return jsonify({"ok": False, "error": "Bad request: " + str(e)}), 400

    if not username or not password:
        return jsonify({"ok": False, "error": "Username and password required"}), 400

    # Check DB connection
    if admins_col is None:
        return jsonify({"ok": False, "error": "Database not connected. Start MongoDB first."}), 503

    # Find admin user
    try:
        admin = admins_col.find_one({"username": username})
    except Exception as e:
        return jsonify({"ok": False, "error": "DB error: " + str(e)}), 500

    if admin:
        stored = admin.get("password")
        try:
            ok = bcrypt.checkpw(password.encode("utf-8"), stored)
        except Exception:
            ok = (stored == password)
        if ok:
            session["admin_logged_in"] = True
            session["admin_user"] = username
            return jsonify({"ok": True, "redirect": "/dashboard"})

    return jsonify({"ok": False, "error": "Wrong username or password"}), 401


@app.route("/login-form", methods=["POST"])
def login_form_fallback():
    """Fallback for inline HTML form when template is missing"""
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if admins_col:
        admin = admins_col.find_one({"username": username})
        if admin:
            stored = admin.get("password")
            try:
                ok = bcrypt.checkpw(password.encode("utf-8"), stored)
            except Exception:
                ok = (stored == password)
            if ok:
                session["admin_logged_in"] = True
                session["admin_user"] = username
                return redirect("/dashboard")
    return redirect("/login")

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "GET":
        return redirect("/login")
    
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
            return redirect("/dashboard")
    
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


# ==================== SHOP ROUTES ====================

@app.route("/shop")
def shop_page():
    return render_template("shop.html")

@app.route("/profile")
def profile_page():
    return render_template("profile.html")

@app.route("/api/shop/products")
def get_shop_products():
    """Get all shop products with optional filters"""
    category = request.args.get("category")
    search = request.args.get("search", "")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    sort_by = request.args.get("sort", "created_at")
    
    query = {"active": True}
    if category and category != "all":
        query["category"] = category
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}}
        ]
    if min_price is not None:
        query.setdefault("price", {})["$gte"] = min_price
    if max_price is not None:
        query.setdefault("price", {})["$lte"] = max_price
    
    sort_map = {"price_asc": [("price", 1)], "price_desc": [("price", -1)],
                "rating": [("avg_rating", -1)], "created_at": [("created_at", -1)]}
    sort_order = sort_map.get(sort_by, [("created_at", -1)])
    
    products = list(shop_products_col.find(query).sort(sort_order))
    for p in products:
        p["_id"] = str(p["_id"])
    return jsonify(products)

@app.route("/api/shop/products/<product_id>")
def get_shop_product(product_id):
    p = shop_products_col.find_one({"_id": ObjectId(product_id)})
    if not p:
        return jsonify({"error": "Not found"}), 404
    p["_id"] = str(p["_id"])
    # get ratings
    ratings = list(shop_ratings_col.find({"product_id": product_id}))
    for r in ratings:
        r["_id"] = str(r["_id"])
        if r.get("created_at"):
            r["created_at"] = r["created_at"].isoformat()
    p["ratings"] = ratings
    return jsonify(p)

@app.route("/api/shop/cart/<user_id>", methods=["GET"])
def get_cart(user_id):
    cart = shop_cart_col.find_one({"user_id": user_id}) or {"items": []}
    if "_id" in cart:
        cart["_id"] = str(cart["_id"])
    return jsonify(cart)

@app.route("/api/shop/cart/<user_id>", methods=["POST"])
def update_cart(user_id):
    payload = request.json or {}
    action = payload.get("action")  # add, remove, update, clear
    product_id = payload.get("product_id")
    qty = payload.get("quantity", 1)
    
    cart = shop_cart_col.find_one({"user_id": user_id})
    if not cart:
        cart = {"user_id": user_id, "items": [], "updated_at": datetime.utcnow()}
    
    items = cart.get("items", [])
    
    if action == "add":
        existing = next((i for i in items if i["product_id"] == product_id), None)
        if existing:
            existing["quantity"] += qty
        else:
            p = shop_products_col.find_one({"_id": ObjectId(product_id)})
            if p:
                items.append({
                    "product_id": product_id,
                    "name": p["name"],
                    "price": p["price"],
                    "image": p.get("image", ""),
                    "quantity": qty
                })
    elif action == "remove":
        items = [i for i in items if i["product_id"] != product_id]
    elif action == "update":
        for i in items:
            if i["product_id"] == product_id:
                i["quantity"] = qty
    elif action == "clear":
        items = []
    
    shop_cart_col.update_one(
        {"user_id": user_id},
        {"$set": {"items": items, "updated_at": datetime.utcnow()}},
        upsert=True
    )
    return jsonify({"status": "ok", "item_count": len(items)})

@app.route("/api/shop/orders", methods=["POST"])
def place_order():
    payload = request.json or {}
    user_id = payload.get("user_id")
    items = payload.get("items", [])
    delivery = payload.get("delivery", {})
    payment_method = payload.get("payment_method", "card")
    
    if not items:
        return jsonify({"error": "No items"}), 400
    
    total = sum(i["price"] * i["quantity"] for i in items)
    order = {
        "user_id": user_id,
        "items": items,
        "total": total,
        "delivery": delivery,
        "payment_method": payment_method,
        "status": "confirmed",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "order_number": f"ORD{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    }
    result = shop_orders_col.insert_one(order)
    # clear cart
    shop_cart_col.update_one({"user_id": user_id}, {"$set": {"items": []}})
    return jsonify({"status": "success", "order_id": str(result.inserted_id), "order_number": order["order_number"], "total": total})

@app.route("/api/shop/orders/<user_id>")
def get_user_orders(user_id):
    orders = list(shop_orders_col.find({"user_id": user_id}).sort("created_at", -1))
    for o in orders:
        o["_id"] = str(o["_id"])
        if o.get("created_at"):
            o["created_at"] = o["created_at"].isoformat()
    return jsonify(orders)

@app.route("/api/shop/ratings", methods=["POST"])
def add_rating():
    payload = request.json or {}
    product_id = payload.get("product_id")
    user_id = payload.get("user_id")
    rating = payload.get("rating", 5)
    review = payload.get("review", "")
    
    # upsert
    shop_ratings_col.update_one(
        {"product_id": product_id, "user_id": user_id},
        {"$set": {"rating": rating, "review": review, "created_at": datetime.utcnow()}},
        upsert=True
    )
    # update product avg
    agg = list(shop_ratings_col.aggregate([
        {"$match": {"product_id": product_id}},
        {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}}
    ]))
    if agg:
        shop_products_col.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"avg_rating": round(agg[0]["avg"], 1), "rating_count": agg[0]["count"]}}
        )
    return jsonify({"status": "ok"})

@app.route("/api/shop/seed", methods=["POST"])
def seed_shop():
    """Seed shop with products"""
    products = [
        {
            "name": "BSc IT Degree Programme", "category": "education",
            "price": 250000, "original_price": 300000,
            "description": "4-year accredited BSc in Information Technology. Covers software engineering, networks, AI, and data science.",
            "image": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&q=80",
            "tags": ["degree", "IT", "university", "4-year"],
            "badge": "Popular", "delivery": ["online", "campus"],
            "duration": "4 Years", "rating_count": 124, "avg_rating": 4.7, "active": True,
            "created_at": datetime.utcnow(), "stock": 50
        },
        {
            "name": "IELTS Preparation Course", "category": "education",
            "price": 35000, "original_price": 45000,
            "description": "Comprehensive IELTS coaching with mock tests, expert tutors, and guaranteed band score improvement.",
            "image": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400&q=80",
            "tags": ["IELTS", "English", "exam", "language"],
            "badge": "Best Seller", "delivery": ["online", "in-person"],
            "duration": "3 Months", "rating_count": 89, "avg_rating": 4.8, "active": True,
            "created_at": datetime.utcnow(), "stock": 100
        },
        {
            "name": "Japan Visa Assistance Package", "category": "visa",
            "price": 15000, "original_price": 20000,
            "description": "Complete Japan visa application support. Includes document review, interview prep, and application submission.",
            "image": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=400&q=80",
            "tags": ["Japan", "visa", "travel", "immigration"],
            "badge": "New", "delivery": ["online"],
            "duration": "2-4 Weeks", "rating_count": 45, "avg_rating": 4.6, "active": True,
            "created_at": datetime.utcnow(), "stock": 200
        },
        {
            "name": "ASUS VivoBook 15 Laptop", "category": "laptops",
            "price": 189000, "original_price": 220000,
            "description": "Intel Core i5, 8GB RAM, 512GB SSD. Perfect for students and professionals. 1-year warranty.",
            "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&q=80",
            "tags": ["laptop", "ASUS", "computer", "student"],
            "badge": "Deal", "delivery": ["delivery", "pickup"],
            "duration": "3-5 Days Delivery", "rating_count": 67, "avg_rating": 4.5, "active": True,
            "created_at": datetime.utcnow(), "stock": 15
        },
        {
            "name": "HP Pavilion Gaming Laptop", "category": "laptops",
            "price": 285000, "original_price": 320000,
            "description": "AMD Ryzen 5, 16GB RAM, RTX 3050, 512GB SSD. Designed for gaming and creative work.",
            "image": "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&q=80",
            "tags": ["laptop", "gaming", "HP", "high-performance"],
            "badge": "Hot", "delivery": ["delivery", "pickup"],
            "duration": "5-7 Days Delivery", "rating_count": 52, "avg_rating": 4.6, "active": True,
            "created_at": datetime.utcnow(), "stock": 8
        },
        {
            "name": "Handwoven Batik Saree - Blue", "category": "fashion",
            "price": 8500, "original_price": 12000,
            "description": "Traditional Sri Lankan handwoven batik saree in vibrant blue. Pure cotton, 5.5 meters. Ideal for formal occasions.",
            "image": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=400&q=80",
            "tags": ["batik", "saree", "fashion", "traditional", "Sri Lanka"],
            "badge": "Handmade", "delivery": ["delivery", "pickup"],
            "duration": "2-3 Days Delivery", "rating_count": 93, "avg_rating": 4.9, "active": True,
            "created_at": datetime.utcnow(), "stock": 30
        },
        {
            "name": "Silk Batik Saree Collection", "category": "fashion",
            "price": 15000, "original_price": 18500,
            "description": "Premium silk batik saree with intricate hand-painted designs. Available in multiple colors.",
            "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=400&q=80",
            "tags": ["silk", "batik", "saree", "premium", "handpainted"],
            "badge": "Premium", "delivery": ["delivery"],
            "duration": "3-5 Days Delivery", "rating_count": 41, "avg_rating": 4.8, "active": True,
            "created_at": datetime.utcnow(), "stock": 20
        },
        {
            "name": "Australia Visa Consultation", "category": "visa",
            "price": 12000, "original_price": None,
            "description": "Expert consultation for Australian student/work/tourist visa. Includes eligibility assessment and document checklist.",
            "image": "https://images.unsplash.com/photo-1523482580672-f109ba8cb9be?w=400&q=80",
            "tags": ["Australia", "visa", "consultation", "immigration"],
            "badge": None, "delivery": ["online", "in-person"],
            "duration": "Consultation 1 Hour", "rating_count": 28, "avg_rating": 4.5, "active": True,
            "created_at": datetime.utcnow(), "stock": 999
        },
        {
            "name": "Lenovo IdeaPad Slim 3", "category": "laptops",
            "price": 145000, "original_price": 165000,
            "description": "Intel Core i3, 8GB RAM, 256GB SSD. Lightweight and affordable for everyday computing.",
            "image": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400&q=80",
            "tags": ["laptop", "Lenovo", "budget", "lightweight"],
            "badge": "Value Pick", "delivery": ["delivery", "pickup"],
            "duration": "3-5 Days Delivery", "rating_count": 78, "avg_rating": 4.4, "active": True,
            "created_at": datetime.utcnow(), "stock": 22
        },
        {
            "name": "Python & Data Science Bootcamp", "category": "education",
            "price": 28000, "original_price": 40000,
            "description": "Intensive 6-week bootcamp covering Python, pandas, machine learning, and real-world projects.",
            "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=400&q=80",
            "tags": ["Python", "data science", "bootcamp", "machine learning"],
            "badge": "Trending", "delivery": ["online"],
            "duration": "6 Weeks", "rating_count": 156, "avg_rating": 4.9, "active": True,
            "created_at": datetime.utcnow(), "stock": 999
        }
    ]
    shop_products_col.delete_many({})
    shop_products_col.insert_many(products)
    return jsonify({"status": "ok", "count": len(products)})


# ==================== USER PROFILE (EXTENDED) ====================

@app.route("/api/user/profile/<user_id>", methods=["GET"])
def get_user_profile(user_id):
    profile = user_profiles_col.find_one({"user_id": user_id})
    if not profile:
        return jsonify({"user_id": user_id})
    profile["_id"] = str(profile["_id"])
    return jsonify(profile)

@app.route("/api/user/profile/<user_id>", methods=["POST"])
def save_user_profile(user_id):
    payload = request.json or {}
    payload["user_id"] = user_id
    payload["updated_at"] = datetime.utcnow()
    user_profiles_col.update_one(
        {"user_id": user_id},
        {"$set": payload},
        upsert=True
    )
    return jsonify({"status": "ok"})

@app.route("/api/user/consent/<user_id>", methods=["GET"])
def get_consent(user_id):
    c = consent_col.find_one({"user_id": user_id})
    if not c:
        return jsonify({"user_id": user_id, "email_marketing": False, "ads": False, "analytics": False, "data_sharing": False})
    c["_id"] = str(c["_id"])
    return jsonify(c)

@app.route("/api/user/consent/<user_id>", methods=["POST"])
def save_consent(user_id):
    payload = request.json or {}
    payload["user_id"] = user_id
    payload["updated_at"] = datetime.utcnow()
    consent_col.update_one({"user_id": user_id}, {"$set": payload}, upsert=True)
    # log consent change
    behavior_col.insert_one({
        "user_id": user_id, "event": "consent_change",
        "data": payload, "timestamp": datetime.utcnow()
    })
    return jsonify({"status": "ok"})

@app.route("/api/user/export/<user_id>")
def export_user_data(user_id):
    """GDPR data export"""
    profile = user_profiles_col.find_one({"user_id": user_id}) or {}
    consent = consent_col.find_one({"user_id": user_id}) or {}
    applications = list(db["applications"].find({"user_id": user_id}))
    orders = list(shop_orders_col.find({"user_id": user_id}))
    behaviors = list(behavior_col.find({"user_id": user_id}).limit(500))
    
    def clean(obj):
        if "_id" in obj: obj["_id"] = str(obj["_id"])
        for k, v in obj.items():
            if isinstance(v, datetime): obj[k] = v.isoformat()
        return obj
    
    export = {
        "exported_at": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "profile": clean(profile),
        "consent": clean(consent),
        "applications": [clean(a) for a in applications],
        "orders": [clean(o) for o in orders],
        "behavior_events": [clean(b) for b in behaviors]
    }
    return jsonify(export)

@app.route("/api/user/delete/<user_id>", methods=["DELETE"])
def delete_user_account(user_id):
    """Delete user account + anonymize engagement/behavior data"""
    # Hard delete personal data
    user_profiles_col.delete_one({"user_id": user_id})
    consent_col.delete_one({"user_id": user_id})
    users_col.delete_one({"user_id": user_id})
    shop_cart_col.delete_one({"user_id": user_id})
    
    # Anonymize (not delete) behavior + engagement
    anon_id = f"deleted_{user_id[:8]}_anon"
    behavior_col.update_many(
        {"user_id": user_id},
        {"$set": {"user_id": anon_id, "anonymized": True}, "$unset": {"ip": "", "device": ""}}
    )
    eng_col.update_many(
        {"user_id": user_id},
        {"$set": {"user_id": anon_id, "anonymized": True}}
    )
    
    # Soft-delete applications
    db["applications"].update_many(
        {"user_id": user_id},
        {"$set": {"user_id": anon_id, "anonymized": True}}
    )
    
    return jsonify({"status": "deleted", "message": "Account deleted and data anonymized"})


# ==================== BEHAVIOR TRACKING ====================

@app.route("/api/behavior", methods=["POST"])
def track_behavior():
    payload = request.json or {}
    payload["timestamp"] = datetime.utcnow()
    payload["ip"] = request.remote_addr
    behavior_col.insert_one(payload)
    return jsonify({"status": "ok"})

@app.route("/api/user/behavior/<user_id>")
def get_behavior_summary(user_id):
    events = list(behavior_col.find({"user_id": user_id}).sort("timestamp", -1).limit(200))
    for e in events:
        e["_id"] = str(e["_id"])
        if e.get("timestamp"): e["timestamp"] = e["timestamp"].isoformat()
    
    # aggregate stats
    from collections import Counter
    event_counts = Counter(e.get("event") for e in events)
    searches = [e.get("query") for e in events if e.get("event") == "search" and e.get("query")]
    
    return jsonify({
        "total_events": len(events),
        "event_counts": dict(event_counts),
        "recent_searches": searches[:10],
        "events": events[:50]
    })


# ==================== SEED TEST USERS ====================

@app.route("/api/seed/users", methods=["POST"])
def seed_test_users():
    """Generate realistic test users"""
    import random
    
    govt_names = ["Kamal Perera", "Suresh Fernando", "Niluka Jayawardena", "Chamara Silva", "Priya Bandara"]
    prof_names = ["Thisara Ratnayake", "Samanthi Wickramasinghe", "Dulith Herath", "Anomi Gunawardena", "Kasun Mendis"]
    parent_names = ["Aruna Dissanayake", "Nirosha Kumari", "Sanath Liyanage", "Dilrukshi Senanayake", "Roshan Pathirana"]
    
    users = []
    
    for i, name in enumerate(govt_names):
        users.append({
            "user_id": f"govt_{i+1:03d}",
            "name": name,
            "type": "government_employee",
            "family": {"marital_status": random.choice(["married", "single"]), "children": random.randint(0, 3), "dependents": random.randint(0, 2)},
            "education": [{"degree": "BA Public Administration", "institution": "University of Sri Jayewardenepura", "year": 2010 + i}],
            "career": {"current_role": "Government Officer", "department": random.choice(["Ministry of Finance", "Dept of Registration", "Land Registry"]), "years_exp": random.randint(5, 20)},
            "interests": random.sample(["IT", "law", "finance", "public policy", "languages"], 3),
            "consent": {"email_marketing": True, "ads": False, "analytics": True, "data_sharing": False},
            "created_at": datetime.utcnow()
        })
    
    for i, name in enumerate(prof_names):
        users.append({
            "user_id": f"prof_{i+1:03d}",
            "name": name,
            "type": "young_professional",
            "family": {"marital_status": random.choice(["single", "married"]), "children": random.randint(0, 1), "dependents": 0},
            "education": [{"degree": "BSc Computer Science", "institution": random.choice(["UCSC", "SLIIT", "IIT"]), "year": 2018 + i % 4}],
            "career": {"current_role": random.choice(["Software Engineer", "Data Analyst", "UX Designer", "Product Manager"]), "company": random.choice(["WSO2", "hSenid", "Virtusa", "99X"]), "years_exp": random.randint(1, 8)},
            "interests": random.sample(["Python", "cloud", "IELTS", "Japan visa", "gaming laptops"], 3),
            "consent": {"email_marketing": True, "ads": True, "analytics": True, "data_sharing": True},
            "created_at": datetime.utcnow()
        })
    
    for i, name in enumerate(parent_names):
        users.append({
            "user_id": f"parent_{i+1:03d}",
            "name": name,
            "type": "parent",
            "family": {"marital_status": "married", "children": random.randint(1, 4), "dependents": random.randint(1, 3)},
            "education": [{"degree": random.choice(["Advanced Level", "HND", "Diploma"]), "institution": "Local College", "year": 2000 + i}],
            "career": {"current_role": random.choice(["Teacher", "Nurse", "Entrepreneur", "Accountant"]), "company": "Various", "years_exp": random.randint(10, 25)},
            "interests": random.sample(["education programs", "batik sarees", "IT courses for children", "visa assistance"], 3),
            "consent": {"email_marketing": random.choice([True, False]), "ads": False, "analytics": True, "data_sharing": False},
            "created_at": datetime.utcnow()
        })
    
    user_profiles_col.delete_many({"user_id": {"$regex": "^(govt|prof|parent)_"}})
    user_profiles_col.insert_many(users)
    
    return jsonify({"status": "ok", "seeded": len(users)})


# ==================== DASHBOARD ====================

@app.route("/dashboard")
def dashboard_page():
    if not session.get("admin_logged_in"):
        return redirect("/login")
    return render_template("dashboard.html")

@app.route("/api/dashboard/stats")
def dashboard_stats():
    """Aggregated stats for the dashboard"""
    if not db:
        return jsonify({"error": "DB not connected"}), 503

    # User stats
    total_users = user_profiles_col.count_documents({})
    user_types = list(user_profiles_col.aggregate([
        {"$group": {"_id": "$type", "count": {"$sum": 1}}}
    ]))

    # Application stats
    total_apps = db["applications"].count_documents({})
    app_by_status = list(db["applications"].aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]))

    # Shop stats
    total_orders = shop_orders_col.count_documents({})
    total_revenue = list(shop_orders_col.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$total"}}}
    ]))
    revenue = total_revenue[0]["total"] if total_revenue else 0

    order_by_status = list(shop_orders_col.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]))

    top_products = list(shop_orders_col.aggregate([
        {"$unwind": "$items"},
        {"$group": {"_id": "$items.name", "count": {"$sum": "$items.quantity"}, "revenue": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]))

    # Behavior stats
    total_events = behavior_col.count_documents({})
    event_types = list(behavior_col.aggregate([
        {"$group": {"_id": "$event", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}, {"$limit": 8}
    ]))

    # Consent stats
    consent_stats = list(consent_col.aggregate([
        {"$group": {
            "_id": None,
            "email_yes": {"$sum": {"$cond": ["$email_marketing", 1, 0]}},
            "ads_yes": {"$sum": {"$cond": ["$ads", 1, 0]}},
            "analytics_yes": {"$sum": {"$cond": ["$analytics", 1, 0]}},
            "sharing_yes": {"$sum": {"$cond": ["$data_sharing", 1, 0]}},
            "total": {"$sum": 1}
        }}
    ]))
    consent = consent_stats[0] if consent_stats else {}

    # Recent activity (last 10 behavior events)
    recent_events = list(behavior_col.find({}).sort("timestamp", -1).limit(10))
    for e in recent_events:
        e["_id"] = str(e["_id"])
        if e.get("timestamp"): e["timestamp"] = e["timestamp"].isoformat()

    # Daily signups (last 7 days)
    from datetime import timedelta
    daily = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        cnt = user_profiles_col.count_documents({"created_at": {"$gte": start, "$lt": end}})
        daily.append({"date": start.strftime("%b %d"), "count": cnt})

    # Top categories clicked
    top_cats = list(eng_col.aggregate([
        {"$match": {"category_id": {"$exists": True}}},
        {"$group": {"_id": "$category_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}, {"$limit": 6}
    ]))

    return jsonify({
        "users": {
            "total": total_users,
            "by_type": {t["_id"]: t["count"] for t in user_types if t["_id"]}
        },
        "applications": {
            "total": total_apps,
            "by_status": {a["_id"]: a["count"] for a in app_by_status if a["_id"]}
        },
        "shop": {
            "total_orders": total_orders,
            "revenue": revenue,
            "by_status": {o["_id"]: o["count"] for o in order_by_status if o["_id"]},
            "top_products": top_products
        },
        "behavior": {
            "total_events": total_events,
            "by_type": {e["_id"]: e["count"] for e in event_types if e["_id"]},
            "recent": recent_events
        },
        "consent": consent,
        "daily_signups": daily,
        "top_categories": top_cats
    })


@app.route("/api/dashboard/users")
def dashboard_users():
    """All user profiles for the user table"""
    users = list(user_profiles_col.find({}).sort("created_at", -1).limit(50))
    for u in users:
        u["_id"] = str(u["_id"])
        if u.get("created_at"): u["created_at"] = u["created_at"].isoformat()
    return jsonify(users)


@app.route("/api/dashboard/orders")
def dashboard_orders():
    """Recent orders"""
    orders = list(shop_orders_col.find({}).sort("created_at", -1).limit(30))
    for o in orders:
        o["_id"] = str(o["_id"])
        if o.get("created_at"): o["created_at"] = o["created_at"].isoformat()
    return jsonify(orders)



# ═══════════════════════════════════════════════════════════════════════════════
#  AUTO-SEED  — runs once on startup when categories collection is empty
# ═══════════════════════════════════════════════════════════════════════════════
def _make_items(prefix, sub_n, sub_name, n=10):
    templates = [
        ("Application",       "Apply for {s}",              ["ID", "Application form"],           "1,000 LKR", "7 days"),
        ("Renewal",           "Renew existing {s}",          ["Current certificate"],              "500 LKR",   "5 days"),
        ("Duplicate Copy",    "Get a duplicate {s}",         ["Police report", "ID"],              "800 LKR",   "5 days"),
        ("Amendment",         "Amend {s} details",           ["Current document", "Proof"],        "600 LKR",   "3 days"),
        ("Transfer",          "Transfer {s} ownership",      ["Both parties NIC", "NOC"],          "1,200 LKR", "10 days"),
        ("Cancellation",      "Cancel {s}",                  ["Original document"],                "300 LKR",   "3 days"),
        ("Verification",      "Verify {s} authenticity",     ["Document copy"],                    "400 LKR",   "2 days"),
        ("Express Service",   "Fast-track {s} processing",   ["Regular requirements","Extra fee"], "2,000 LKR", "1 day"),
        ("Online Submission", "Online {s} submission",       ["Digital documents", "Email"],       "900 LKR",   "5 days"),
        ("Status Check",      "Check {s} application status",["Application number"],              "Free",      "Immediate"),
    ]
    return [{
        "id": f"{prefix}_{sub_n}_{i+1}",
        "title": {"en": f"{t[0]} — {sub_name}", "si": f"{t[0]} — {sub_name}", "ta": f"{t[0]} — {sub_name}"},
        "description": {"en": t[1].format(s=sub_name.lower()), "si": t[1].format(s=sub_name.lower()), "ta": t[1].format(s=sub_name.lower())},
        "requirements": t[2],
        "fee": t[3], "processingTime": t[4],
        "formFields": [
            {"name":"fullName","type":"text","required":True},
            {"name":"nicNumber","type":"text","required":True},
            {"name":"contactNumber","type":"tel","required":True},
            {"name":"emailAddress","type":"email","required":False},
        ], "status":"active"
    } for i,t in enumerate(templates[:n])]

def _sub(prefix, idx, name, kws):
    return {
        "id": f"sub_{prefix}_{idx+1}",
        "name": {"en": name, "si": name, "ta": name},
        "description": f"Services related to {name.lower()}",
        "keywords": kws, "itemCount": 10,
        "items": _make_items(prefix, idx+1, name, 10)
    }

def seed_portal_data():
    if categories_col is None:
        return
    if categories_col.count_documents({}) > 0:
        print("✅ Portal data already seeded")
        return
    print("🌱 Auto-seeding portal categories…")
    DEFS = [
      ("cat_it","IT & Digital Services","තොරතුරු තාක්ෂණය","தகவல் தொழில்நுட்பம்","💻","#1976D2","it",[
        ("Digital Certificates",["certificate","ssl"]),("Software Development",["software","dev"]),
        ("Cloud Services",["cloud","hosting"]),("Cybersecurity",["security","firewall"]),
        ("IT Training",["training","course"]),("Technical Support",["support","help"]),
        ("Web Development",["web","website"]),("Mobile Applications",["mobile","app"]),
        ("Data Analytics",["data","analytics"]),("Network Infrastructure",["network","lan"]),
        ("Database Management",["database","sql"]),("DevOps Services",["devops","ci/cd"]),
        ("AI/ML Services",["ai","ml"]),("Hardware Services",["hardware","repair"]),
        ("IT Consulting",["consulting","advisory"]),
      ]),
      ("cat_health","Health & Medical","සෞඛ්‍ය හා වෛද්‍ය","சுகாதாரம்","🏥","#D32F2F","health",[
        ("Medical Certificates",["medical","certificate"]),("Vaccinations",["vaccine","immunization"]),
        ("Hospital Services",["hospital","admission"]),("Pharmacy Services",["pharmacy","medicine"]),
        ("Mental Health",["mental","counseling"]),("Dental Services",["dental","teeth"]),
        ("Eye Care",["eye","vision"]),("Maternity Services",["maternity","pregnancy"]),
        ("Child Healthcare",["child","pediatric"]),("Elderly Care",["elderly","senior"]),
        ("Emergency Services",["emergency","ambulance"]),("Medical Tests",["test","lab"]),
        ("Health Insurance",["insurance","coverage"]),("Medical Records",["records","history"]),
        ("Telemedicine",["telemedicine","online"]),
      ]),
      ("cat_education","Education & Learning","අධ්‍යාපනය","கல்வி","📚","#4CAF50","edu",[
        ("School Admission",["school","admission"]),("University Admission",["university","degree"]),
        ("Scholarships",["scholarship","grant"]),("Online Courses",["online","elearning"]),
        ("Vocational Training",["vocational","skills"]),("Language Courses",["language","english"]),
        ("Exam Registration",["exam","test"]),("Educational Certificates",["certificate","diploma"]),
        ("Student Loans",["loan","education"]),("Educational Materials",["books","materials"]),
        ("Tutoring Services",["tutor","coaching"]),("Distance Learning",["distance","remote"]),
        ("Special Education",["special needs","disability"]),("Adult Education",["adult","lifelong"]),
        ("Professional Development",["professional","training"]),
      ]),
      ("cat_transport","Transport & Vehicles","ප්‍රවාහනය","போக்குவரத்து","🚗","#FF6B35","transport",[
        ("Driving Licenses",["license","driving"]),("Vehicle Registration",["registration","vehicle"]),
        ("Revenue Licenses",["revenue","road tax"]),("Vehicle Insurance",["insurance","coverage"]),
        ("Parking Permits",["parking","permit"]),("Route Permits",["route","commercial"]),
        ("Vehicle Inspection",["inspection","emission"]),("Traffic Fines",["fine","penalty"]),
        ("Public Transport",["bus","train"]),("Taxi Services",["taxi","cab"]),
        ("Vehicle Transfer",["transfer","ownership"]),("Import Permits",["import","customs"]),
        ("Emission Testing",["emission","pollution"]),("Road Tax",["tax","road"]),
        ("Vehicle Modifications",["modification","upgrade"]),
      ]),
      ("cat_land","Land & Housing","ඉඩම් හා නිවාස","நிலம் & வீடு","🏘️","#795548","land",[
        ("Property Deeds",["deed","title"]),("Building Permits",["building","construction"]),
        ("Land Survey",["survey","boundary"]),("Property Tax",["tax","valuation"]),
        ("Construction Approvals",["approval","planning"]),("Housing Loans",["loan","mortgage"]),
        ("Rental Agreements",["rental","lease"]),("Land Registration",["registration","records"]),
        ("Property Transfer",["transfer","sale"]),("Utility Connections",["utility","water"]),
        ("Property Valuation",["valuation","appraisal"]),("Zoning Permits",["zoning","land use"]),
        ("Renovation Permits",["renovation","alteration"]),("Land Development",["development","subdivision"]),
        ("Property Insurance",["insurance","protection"]),
      ]),
      ("cat_civil","Civil Registry","සිවිල් රෙජිස්ට්‍රි","சிவில் பதிவு","📄","#0288D1","civil",[
        ("Birth Registration",["birth","certificate"]),("Death Registration",["death","certificate"]),
        ("Marriage Registration",["marriage","wedding"]),("Divorce Certificates",["divorce","separation"]),
        ("Name Change",["name","change"]),("NIC Application",["nic","identity"]),
        ("Smart NIC (eNIC)",["smart nic","biometric"]),("Passport — New",["passport","new"]),
        ("Passport — Renewal",["passport","renew"]),("Passport — Urgent",["passport","urgent"]),
        ("Visa Services",["visa","foreign"]),("Dual Citizenship",["dual citizenship"]),
        ("Certificate Apostille",["apostille","legalisation"]),("Police Clearance",["clearance","conduct"]),
        ("Emergency Travel Docs",["emergency","lost passport"]),
      ]),
      ("cat_business","Business & Trade","ව්‍යාපාර","வணிகம்","💼","#0284c7","biz",[
        ("Business Registration",["business","company"]),("Trade Licenses",["trade","license"]),
        ("Tax Registration",["tax","vat"]),("Export Permits",["export","trade"]),
        ("Import Licenses",["import","customs"]),("Patents & IP",["patent","trademark"]),
        ("Company Amendments",["amendment","director"]),("Annual Returns",["annual","compliance"]),
        ("Labour Registration",["labour","employee"]),("EPF/ETF",["epf","etf"]),
        ("Trade Mark Registration",["trademark","brand"]),("Factory Permits",["factory","manufacturing"]),
        ("Food Safety Licenses",["food","safety"]),("Environmental Permits",["environment","clearance"]),
        ("Company Deregistration",["deregister","close"]),
      ]),
      ("cat_welfare","Social Welfare","සමාජ සුභසාධන","சமூக நலன்","🤝","#be185d","welfare",[
        ("Samurdhi Benefits",["samurdhi","subsidy"]),("Disability Allowance",["disability","allowance"]),
        ("Elderly Pension",["pension","elderly"]),("Child Protection",["child","protection"]),
        ("Women Empowerment",["women","empowerment"]),("Food Stamps",["food","stamps"]),
        ("Housing Assistance",["housing","shelter"]),("Funeral Assistance",["funeral","burial"]),
        ("Flood Relief",["flood","disaster"]),("Medical Assistance",["medical","assistance"]),
        ("Orphan Benefits",["orphan","child"]),("Youth Development",["youth","training"]),
        ("Community Development",["community","village"]),("Volunteer Registration",["volunteer","NGO"]),
        ("Social Insurance",["insurance","social"]),
      ]),
      ("cat_agriculture","Agriculture","කෘෂිකර්මය","விவசாயம்","🌾","#65a30d","agri",[
        ("Farm Registration",["farm","agriculture"]),("Fertiliser Subsidy",["fertiliser","subsidy"]),
        ("Crop Insurance",["crop","insurance"]),("Irrigation Permits",["irrigation","water"]),
        ("Pesticide Permits",["pesticide","chemical"]),("Agricultural Loans",["loan","farming"]),
        ("Seed Certification",["seed","quality"]),("Animal Health",["animal","veterinary"]),
        ("Fisheries Licenses",["fisheries","fishing"]),("Export Certification",["export","quality"]),
        ("Organic Certification",["organic","eco"]),("Farm Machinery",["machinery","tractor"]),
        ("Market Access",["market","wholesale"]),("Agri Training",["training","extension"]),
        ("Disaster Relief",["disaster","drought"]),
      ]),
      ("cat_elections","Elections & Civic","මැතිවරණ","தேர்தல்","🗳️","#9C27B0","elect",[
        ("Voter Registration",["voter","register"]),("Voter ID Card",["voter","id"]),
        ("Electoral Roll",["roll","list"]),("Candidate Nomination",["candidate","nomination"]),
        ("Postal Voting",["postal","vote"]),("Election Complaints",["complaint","fraud"]),
        ("Constituency Info",["constituency","ward"]),("Election Results",["results","tally"]),
        ("Campaign Registration",["campaign","party"]),("Referendum Info",["referendum","poll"]),
        ("Election Observers",["observer","monitor"]),("Polling Station",["polling","location"]),
        ("Election Calendar",["calendar","dates"]),("Civic Education",["civic","democracy"]),
        ("Party Registration",["party","political"]),
      ]),
      ("cat_police","Police & Safety","පොලිසිය","காவல்துறை","🚔","#475569","police",[
        ("Police Clearance",["clearance","conduct"]),("Complaint Filing",["complaint","report"]),
        ("Lost Property",["lost","found"]),("Firearms Permit",["firearm","gun"]),
        ("Crowd Control Permit",["event","gathering"]),("Noise Permits",["noise","event"]),
        ("Victim Assistance",["victim","support"]),("Traffic Accident Report",["accident","report"]),
        ("Missing Persons",["missing","search"]),("Drug Enforcement",["drug","narcotics"]),
        ("Cyber Crime",["cyber","fraud"]),("DNA Testing",["dna","forensic"]),
        ("Witness Protection",["witness","safety"]),("Security Licences",["security","guard"]),
        ("Border Control",["border","immigration"]),
      ]),
      ("cat_tourism","Tourism & Culture","සංචාරක","சுற்றுலா","✈️","#0369a1","tourism",[
        ("Visa on Arrival",["visa","tourist"]),("ETA Application",["eta","electronic"]),
        ("Tourist Permits",["tourist","permit"]),("Hotel Registration",["hotel","accommodation"]),
        ("Tour Guide Licences",["guide","tour"]),("Heritage Sites",["heritage","museum"]),
        ("National Parks",["park","wildlife"]),("Beach Permits",["beach","coastal"]),
        ("Cultural Events",["event","festival"]),("Archaeological Sites",["archaeology","ruins"]),
        ("Tourism Grants",["grant","promotion"]),("Film Permits",["film","media"]),
        ("Adventure Sports",["adventure","sport"]),("Food Tourism",["food","culinary"]),
        ("Eco Tourism",["eco","sustainable"]),
      ]),
    ]
    docs = []
    for (cid,en,si,ta,icon,color,prefix,subs) in DEFS:
        docs.append({
            "id":cid,"name":{"en":en,"si":si,"ta":ta},
            "description":f"{en} government services","icon":icon,"color":color,
            "subcategories":[_sub(prefix,i,s[0],s[1]) for i,s in enumerate(subs)]
        })
    categories_col.insert_many(docs)
    total_subs  = sum(len(d["subcategories"]) for d in docs)
    total_items = sum(len(s["items"]) for d in docs for s in d["subcategories"])
    print(f"✅ Seeded {len(docs)} categories, {total_subs} subcategories, {total_items} service items")

# ensure at least one admin user exists (hashed)
if __name__ == "__main__":
    if admins_col is not None:
        # Always ensure admin user exists with known credentials
        ADMIN_USER = os.getenv("ADMIN_USER", "admin")
        ADMIN_PWD  = os.getenv("ADMIN_PWD",  "Admin@1234")
        hashed = bcrypt.hashpw(ADMIN_PWD.encode("utf-8"), bcrypt.gensalt())
        admins_col.update_one(
            {"username": ADMIN_USER},
            {"$set": {"username": ADMIN_USER, "password": hashed}},
            upsert=True
        )
        print(f"✅ Admin ready — username: {ADMIN_USER}  password: {ADMIN_PWD}")
        seed_portal_data()
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT",5000)))