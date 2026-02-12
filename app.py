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
    services_col = db["services"]       
    subservices_col = db["subservices"]
    admins_col = db["admins"]
    eng_col = db["engagements"]
    categories_col = db["categories"]   
    officers_col = db["officers"]       
    ads_col = db["ads"]                 
    users_col = db["users"]             
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
    """
    Returns all categories with their subcategories.
    Each subcategory includes itemCount for display.
    """
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

@app.route("/api/category/<category_id>")
def get_category(category_id):
    """Get a specific category with all its subcategories"""
    cat = categories_col.find_one({"id": category_id}, {"_id":0})
    return jsonify(cat or {})

@app.route("/api/subcategory/<subcategory_id>")
def get_subcategory(subcategory_id):
    """
    Get details about a specific subcategory including its items.
    This searches through all categories to find the matching subcategory.
    """
    # Find the category that contains this subcategory
    category = categories_col.find_one(
        {"subcategories.id": subcategory_id},
        {"_id": 0}
    )
    
    if not category:
        return jsonify({"error": "Subcategory not found"}), 404
    
    # Extract the specific subcategory
    subcategory = next(
        (sub for sub in category.get("subcategories", []) if sub["id"] == subcategory_id),
        None
    )
    
    if not subcategory:
        return jsonify({"error": "Subcategory not found"}), 404
    
    # Add parent category info
    result = {
        **subcategory,
        "parentCategory": {
            "id": category["id"],
            "name": category["name"],
            "icon": category.get("icon"),
            "color": category.get("color")
        }
    }
    
    return jsonify(result)

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
    
    # Search across categories, subcategories, and services
    regex = {"$regex": q, "$options": "i"}
    results = []
    
    # Search in categories
    for cat in categories_col.find({"$or":[{"name.en":regex}, {"description":regex}]}, {"_id":0}).limit(10):
        results.append({
            "type": "category",
            "id": cat["id"],
            "name": cat["name"],
            "icon": cat.get("icon", "📁")
        })
    
    # Search in subcategories
    for cat in categories_col.find(
        {"subcategories": {"$elemMatch": {"$or": [{"name.en": regex}, {"description": regex}]}}},
        {"_id": 0, "id": 1, "name": 1, "icon": 1, "subcategories": 1}
    ).limit(10):
        for sub in cat.get("subcategories", []):
            if q.lower() in str(sub.get("name", {}).get("en", "")).lower() or \
               q.lower() in str(sub.get("description", "")).lower():
                results.append({
                    "type": "subcategory",
                    "id": sub["id"],
                    "name": sub["name"],
                    "parentCategory": cat["name"],
                    "parentIcon": cat.get("icon", "📁")
                })
    
    return jsonify(results[:20])

# Engagement logging (extended to include subcategory clicks)
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
        "category_id": payload.get("category_id"),
        "subcategory_id": payload.get("subcategory_id"),
        "ad": payload.get("ad"),
        "source": payload.get("source"),
        "timestamp": datetime.utcnow()
    }
    eng_col.insert_one(doc)
    return jsonify({"status":"ok"})

# Progressive profile: save step-by-step partial profile
@app.route("/api/profile/step", methods=["POST"])
def profile_step():
    payload = request.json or {}
    profile_id = payload.get("profile_id") or None
    email = payload.get("email")
    data = payload.get("data",{})
    
    if profile_id:
        users_col.update_one(
            {"_id": ObjectId(profile_id)}, 
            {"$set": {"profile."+payload.get("step", "unknown"): data, "updated": datetime.utcnow()}}, 
            upsert=True
        )
        return jsonify({"status":"ok", "profile_id":profile_id})
    
    if email:
        res = users_col.find_one_and_update(
            {"email":email}, 
            {"$set": {"profile."+payload.get("step","unknown"): data, "updated": datetime.utcnow()}}, 
            upsert=True, 
            return_document=True
        )
        return jsonify({"status":"ok", "profile_id": str(res.get("_id"))})
    
    # fallback - create anonymous
    new_id = users_col.insert_one({
        "profile": {payload.get("step","unknown"):data}, 
        "created":datetime.utcnow()
    }).inserted_id
    return jsonify({"status":"ok", "profile_id": str(new_id)})

# Ads
@app.route("/api/ads")
def get_ads():
    ads = list(ads_col.find({}, {"_id":0}))
    return jsonify(ads)

# --- AI / vector index endpoints ---
def build_vector_index():
    """
    Build or rebuild a FAISS index from categories and subcategories.
    """
    os.makedirs("data", exist_ok=True)
    docs = []
    
    # Index all subcategories with their parent category context
    for cat in categories_col.find():
        cat_id = cat.get("id")
        cat_name = cat.get("name", {}).get("en") or cat.get("name")
        cat_desc = cat.get("description", "")
        
        for sub in cat.get("subcategories", []):
            sub_id = sub.get("id")
            sub_name = sub.get("name", {}).get("en") or sub.get("name")
            sub_desc = sub.get("description", "")
            keywords = " ".join(sub.get("keywords", []))
            
            content = f"{cat_name} | {sub_name} | {sub_desc} | {keywords}"
            
            docs.append({
                "doc_id": f"{cat_id}::{sub_id}",
                "category_id": cat_id,
                "subcategory_id": sub_id,
                "title": sub_name,
                "content": content,
                "metadata": {
                    "category_name": cat_name,
                    "subcategory_name": sub_name,
                    "description": sub_desc,
                    "keywords": sub.get("keywords", []),
                    "itemCount": sub.get("itemCount", 0)
                }
            })
    
    if not docs:
        return {"count": 0, "faiss": FAISS_AVAILABLE, "error": "No data to index"}
    
    model = get_embedding_model()
    texts = [d["content"] for d in docs]
    embeddings = model.encode(texts, show_progress_bar=False)
    embeddings = np.array(embeddings).astype('float32')
    
    if FAISS_AVAILABLE:
        index = faiss.IndexFlatL2(VECTOR_DIM)
        index.add(embeddings)
        faiss.write_index(index, str(INDEX_PATH))
    
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    
    return {"count": len(docs), "faiss": FAISS_AVAILABLE}

def search_vector_index(query, top_k=5):
    """Search the vector index for relevant subcategories"""
    if not META_PATH.exists():
        return {"error": "Index not built yet"}
    
    with open(META_PATH, "r", encoding="utf-8") as f:
        docs = json.load(f)
    
    model = get_embedding_model()
    q_emb = model.encode([query], show_progress_bar=False)
    q_emb = np.array(q_emb).astype('float32')
    
    if FAISS_AVAILABLE and INDEX_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))
        D, I = index.search(q_emb, top_k)
        results = [docs[i] for i in I[0] if i < len(docs)]
    else:
        # Fallback: simple text matching
        results = []
        q_lower = query.lower()
        for doc in docs:
            if q_lower in doc["content"].lower():
                results.append(doc)
            if len(results) >= top_k:
                break
    
    return results[:top_k]

@app.route("/api/ai/search", methods=["POST"])
def ai_search():
    """AI-powered search endpoint"""
    payload = request.json or {}
    query = payload.get("query", "").strip()
    top_k = payload.get("top_k", 5)
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    results = search_vector_index(query, top_k)
    
    if isinstance(results, dict) and "error" in results:
        return jsonify(results), 500
    
    # Format response
    answer = "I found these relevant services:\n\n"
    for i, doc in enumerate(results, 1):
        meta = doc.get("metadata", {})
        answer += f"{i}. **{meta.get('subcategory_name', 'Unknown')}** "
        answer += f"(in {meta.get('category_name', 'Unknown')})\n"
        answer += f"   {meta.get('description', '')}\n"
        if meta.get('keywords'):
            answer += f"   Keywords: {', '.join(meta['keywords'][:3])}\n"
        answer += "\n"
    
    return jsonify({
        "answer": answer,
        "results": results,
        "query": query
    })

@app.route("/api/admin/build_index", methods=["POST"])
@admin_required
def rebuild_index():
    """Admin endpoint to rebuild the vector index"""
    result = build_vector_index()
    return jsonify(result)

# --- Admin auth ---
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

# --- Admin CRUD: services, categories, subcategories, officers, ads ---
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
        if not cid: 
            return jsonify({"error":"id required"}), 400
        
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

# Update subcategory
@app.route("/api/admin/categories/update-subcategory", methods=["POST"])
@admin_required
def update_subcategory():
    payload = request.json
    parent_id = payload.get("parentId")
    subcategory_id = payload.get("subcategoryId")
    updates = payload.get("updates")
    
    if not parent_id or not subcategory_id or not updates:
        return jsonify({"error":"Missing required fields"}), 400
    
    # Update the specific subcategory in the array
    update_fields = {f"subcategories.$.{k}": v for k, v in updates.items()}
    
    categories_col.update_one(
        {"id": parent_id, "subcategories.id": subcategory_id},
        {"$set": update_fields}
    )
    return jsonify({"status":"ok"})

# Delete subcategory
@app.route("/api/admin/categories/delete-subcategory", methods=["POST"])
@admin_required
def delete_subcategory():
    payload = request.json
    parent_id = payload.get("parentId")
    subcategory_id = payload.get("subcategoryId")
    
    if not parent_id or not subcategory_id:
        return jsonify({"error":"parentId and subcategoryId required"}), 400
    
    categories_col.update_one(
        {"id": parent_id},
        {"$pull": {"subcategories": {"id": subcategory_id}}}
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
        if not oid: 
            return jsonify({"error":"id required"}), 400
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
        if not aid: 
            return jsonify({"error":"id required"}), 400
        ads_col.update_one({"id":aid}, {"$set":payload}, upsert=True)
        return jsonify({"status":"ok"})
    
    if request.method == "DELETE":
        aid = request.args.get("id")
        ads_col.delete_one({"id":aid})
        return jsonify({"status":"deleted"})

# --- Admin insights (extended with subcategory analytics) ---
@app.route("/api/admin/insights")
@admin_required
def admin_insights():
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
    categories = {}
    subcategories = {}
    
    for e in eng_col.find({}, {"job":1,"service":1,"question_clicked":1,"desires":1,"category_id":1,"subcategory_id":1}):
        j = (e.get("job") or "Unknown").strip()
        jobs[j] = jobs.get(j,0) + 1
        
        s = e.get("service") or "Unknown"
        services[s] = services.get(s,0) + 1
        
        q = e.get("question_clicked") or "Unknown"
        questions[q] = questions.get(q,0) + 1
        
        for d in e.get("desires") or []:
            desires[d] = desires.get(d,0) + 1
        
        cat_id = e.get("category_id")
        if cat_id:
            categories[cat_id] = categories.get(cat_id, 0) + 1
        
        sub_id = e.get("subcategory_id")
        if sub_id:
            subcategories[sub_id] = subcategories.get(sub_id, 0) + 1
    
    # premium suggestions
    pipeline = [
        {"$group": {"_id": {"user":"$user_id","question":"$question_clicked"}, "count":{"$sum":1}}},
        {"$match": {"count": {"$gte": 2}}}
    ]
    repeated = list(eng_col.aggregate(pipeline))
    premium_suggestions = [
        {"user": r["_id"]["user"], "question": r["_id"]["question"], "count": r["count"]} 
        for r in repeated if r["_id"]["user"]
    ]
    
    return jsonify({
        "age_groups": age_groups,
        "jobs": jobs,
        "services": services,
        "questions": questions,
        "desires": desires,
        "categories": categories,
        "subcategories": subcategories,
        "premium_suggestions": premium_suggestions
    })

# Subcategory Analytics Report
@app.route("/api/admin/subcategory-report")
@admin_required
def subcategory_report():
    """
    Detailed analytics for subcategories including:
    - Most viewed subcategories
    - Engagement by category
    - Time-based trends
    - User demographics per subcategory
    """
    
    # Get all categories for reference
    all_categories = list(categories_col.find({}, {"_id":0}))
    category_map = {c["id"]: c for c in all_categories}
    
    # Subcategory engagement stats
    subcategory_stats = {}
    
    for e in eng_col.find({"subcategory_id": {"$exists": True}}):
        sub_id = e.get("subcategory_id")
        if not sub_id:
            continue
        
        if sub_id not in subcategory_stats:
            subcategory_stats[sub_id] = {
                "total_views": 0,
                "unique_users": set(),
                "age_groups": {"<18":0, "18-25":0, "26-40":0, "41-60":0, "60+":0},
                "jobs": {},
                "timestamps": []
            }
        
        stat = subcategory_stats[sub_id]
        stat["total_views"] += 1
        
        user_id = e.get("user_id")
        if user_id:
            stat["unique_users"].add(user_id)
        
        age = e.get("age")
        if age:
            try:
                age = int(age)
                if age < 18: stat["age_groups"]["<18"] += 1
                elif age <= 25: stat["age_groups"]["18-25"] += 1
                elif age <= 40: stat["age_groups"]["26-40"] += 1
                elif age <= 60: stat["age_groups"]["41-60"] += 1
                else: stat["age_groups"]["60+"] += 1
            except:
                pass
        
        job = e.get("job")
        if job:
            stat["jobs"][job] = stat["jobs"].get(job, 0) + 1
        
        if e.get("timestamp"):
            stat["timestamps"].append(e["timestamp"])
    
    # Build detailed report
    report = []
    for sub_id, stats in subcategory_stats.items():
        # Find parent category and subcategory details
        parent_cat = None
        sub_details = None
        
        for cat_id, cat in category_map.items():
            for sub in cat.get("subcategories", []):
                if sub.get("id") == sub_id:
                    parent_cat = cat
                    sub_details = sub
                    break
            if sub_details:
                break
        
        if not sub_details:
            continue
        
        report.append({
            "subcategory_id": sub_id,
            "subcategory_name": sub_details.get("name", {}).get("en", sub_id),
            "category_id": parent_cat.get("id") if parent_cat else None,
            "category_name": parent_cat.get("name", {}).get("en", "Unknown") if parent_cat else "Unknown",
            "category_icon": parent_cat.get("icon", "📁") if parent_cat else "📁",
            "category_color": parent_cat.get("color", "#0b3b8c") if parent_cat else "#0b3b8c",
            "total_views": stats["total_views"],
            "unique_users": len(stats["unique_users"]),
            "age_groups": stats["age_groups"],
            "top_jobs": sorted(stats["jobs"].items(), key=lambda x: x[1], reverse=True)[:5],
            "item_count": sub_details.get("itemCount", 0),
            "keywords": sub_details.get("keywords", [])
        })
    
    # Sort by total views
    report.sort(key=lambda x: x["total_views"], reverse=True)
    
    return jsonify(report)

# Category-wise subcategory report
@app.route("/api/admin/category-subcategories/<category_id>")
@admin_required
def category_subcategories_report(category_id):
    """Get detailed report for all subcategories within a specific category"""
    
    category = categories_col.find_one({"id": category_id}, {"_id": 0})
    if not category:
        return jsonify({"error": "Category not found"}), 404
    
    subcategories_report = []
    
    for sub in category.get("subcategories", []):
        sub_id = sub.get("id")
        
        # Get engagement stats for this subcategory
        engagement_count = eng_col.count_documents({"subcategory_id": sub_id})
        unique_users = len(eng_col.distinct("user_id", {"subcategory_id": sub_id, "user_id": {"$ne": None}}))
        
        subcategories_report.append({
            "id": sub_id,
            "name": sub.get("name", {}),
            "description": sub.get("description", ""),
            "keywords": sub.get("keywords", []),
            "item_count": sub.get("itemCount", 0),
            "engagement_count": engagement_count,
            "unique_users": unique_users
        })
    
    # Sort by engagement
    subcategories_report.sort(key=lambda x: x["engagement_count"], reverse=True)
    
    return jsonify({
        "category": {
            "id": category["id"],
            "name": category.get("name", {}),
            "icon": category.get("icon", "📁"),
            "color": category.get("color", "#0b3b8c")
        },
        "subcategories": subcategories_report,
        "total_subcategories": len(subcategories_report),
        "total_engagement": sum(s["engagement_count"] for s in subcategories_report)
    })

# Export subcategory report as CSV
@app.route("/api/admin/export_subcategory_report")
@admin_required
def export_subcategory_report():
    """Export detailed subcategory analytics as CSV"""
    
    # Get the report data
    all_categories = list(categories_col.find({}, {"_id":0}))
    category_map = {c["id"]: c for c in all_categories}
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow([
        "Subcategory ID", "Subcategory Name", "Category", 
        "Total Views", "Unique Users", "Item Count",
        "Age <18", "Age 18-25", "Age 26-40", "Age 41-60", "Age 60+",
        "Top Job 1", "Top Job 2", "Top Job 3", "Keywords"
    ])
    
    # Get subcategory stats
    subcategory_stats = {}
    for e in eng_col.find({"subcategory_id": {"$exists": True}}):
        sub_id = e.get("subcategory_id")
        if not sub_id:
            continue
        
        if sub_id not in subcategory_stats:
            subcategory_stats[sub_id] = {
                "views": 0,
                "users": set(),
                "age_groups": {"<18":0, "18-25":0, "26-40":0, "41-60":0, "60+":0},
                "jobs": {}
            }
        
        stat = subcategory_stats[sub_id]
        stat["views"] += 1
        
        if e.get("user_id"):
            stat["users"].add(e["user_id"])
        
        age = e.get("age")
        if age:
            try:
                age = int(age)
                if age < 18: stat["age_groups"]["<18"] += 1
                elif age <= 25: stat["age_groups"]["18-25"] += 1
                elif age <= 40: stat["age_groups"]["26-40"] += 1
                elif age <= 60: stat["age_groups"]["41-60"] += 1
                else: stat["age_groups"]["60+"] += 1
            except:
                pass
        
        if e.get("job"):
            stat["jobs"][e["job"]] = stat["jobs"].get(e["job"], 0) + 1
    
    # Write data
    for cat in all_categories:
        for sub in cat.get("subcategories", []):
            sub_id = sub.get("id")
            stats = subcategory_stats.get(sub_id, {
                "views": 0, "users": set(), 
                "age_groups": {"<18":0, "18-25":0, "26-40":0, "41-60":0, "60+":0},
                "jobs": {}
            })
            
            top_jobs = sorted(stats["jobs"].items(), key=lambda x: x[1], reverse=True)[:3]
            top_job_names = [j[0] for j in top_jobs] + ["", "", ""]
            
            cw.writerow([
                sub_id,
                sub.get("name", {}).get("en", sub_id),
                cat.get("name", {}).get("en", "Unknown"),
                stats["views"],
                len(stats["users"]),
                sub.get("itemCount", 0),
                stats["age_groups"]["<18"],
                stats["age_groups"]["18-25"],
                stats["age_groups"]["26-40"],
                stats["age_groups"]["41-60"],
                stats["age_groups"]["60+"],
                top_job_names[0],
                top_job_names[1],
                top_job_names[2],
                ", ".join(sub.get("keywords", []))
            ])
    
    si.seek(0)
    return send_file(
        StringIO(si.read()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="subcategory_report.csv"
    )

@app.route("/api/admin/engagements")
@admin_required
def admin_engagements():
    items = []
    for e in eng_col.find().sort("timestamp",-1).limit(500):
        e["_id"] = str(e["_id"])
        if e.get("timestamp"):
            e["timestamp"] = e["timestamp"].isoformat()
        items.append(e)
    return jsonify(items)

# CSV export
@app.route("/api/admin/export_csv")
@admin_required
def export_csv():
    cursor = eng_col.find()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow([
        "user_id","age","job","desire","question","service",
        "category_id","subcategory_id","ad","source","timestamp"
    ])
    for e in cursor:
        cw.writerow([
            e.get("user_id"), e.get("age"), e.get("job"),
            ",".join(e.get("desires") or []),
            e.get("question_clicked"), e.get("service"),
            e.get("category_id"), e.get("subcategory_id"),
            e.get("ad"), e.get("source"),
            e.get("timestamp").isoformat() if e.get("timestamp") else ""
        ])
    si.seek(0)
    return send_file(
        StringIO(si.read()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="engagements.csv"
    )

# ensure at least one admin user exists (hashed)
if __name__ == "__main__":
    if admins_col is not None and admins_col.count_documents({}) == 0:
        pwd = os.getenv("ADMIN_PWD","admin123")
        hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
        admins_col.insert_one({"username":"admin","password": hashed})
        print("✓ Admin user created (username: admin)")
    
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT",5000)))