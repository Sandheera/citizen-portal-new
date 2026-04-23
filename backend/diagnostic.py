"""
COMPLETE DIAGNOSTIC SCRIPT
Run this to find ALL issues with your system
"""

import os
from pymongo import MongoClient

print("=" * 60)
print("🔍 CITIZEN PORTAL DIAGNOSTIC TOOL")
print("=" * 60)

# Check MongoDB
print("\n1️⃣ Checking MongoDB Connection...")
try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("   ✅ MongoDB is running")
    
    db = client["citizen_portal"]
    
    # Check collections
    print("\n2️⃣ Checking Database Collections...")
    collections = db.list_collection_names()
    print(f"   Found collections: {', '.join(collections)}")
    
    # Check categories
    cat_count = db.categories.count_documents({})
    print(f"\n3️⃣ Categories: {cat_count}")
    
    if cat_count > 0:
        # Count subcategories
        pipeline = [
            {"$unwind": "$subcategories"},
            {"$group": {"_id": None, "count": {"$sum": 1}}}
        ]
        sub_result = list(db.categories.aggregate(pipeline))
        sub_count = sub_result[0]['count'] if sub_result else 0
        print(f"   Subcategories: {sub_count}")
        
        # Count services
        pipeline = [
            {"$unwind": "$subcategories"},
            {"$unwind": "$subcategories.items"},
            {"$group": {"_id": None, "count": {"$sum": 1}}}
        ]
        item_result = list(db.categories.aggregate(pipeline))
        item_count = item_result[0]['count'] if item_result else 0
        print(f"   Service Items: {item_count}")
        
        # Show categories
        print(f"\n4️⃣ Categories in database:")
        for cat in db.categories.find({}, {"id": 1, "name": 1, "subcategories": 1}):
            print(f"   • {cat['name']['en']} ({len(cat.get('subcategories', []))} subcategories)")
    else:
        print("   ❌ NO CATEGORIES FOUND!")
        print("   → Run: python mega_seed_15_categories.py")
    
    # Check applications
    app_count = db.applications.count_documents({})
    print(f"\n5️⃣ Applications: {app_count}")
    
    if app_count > 0:
        print("   Recent applications:")
        for app in db.applications.find().sort("submitted_at", -1).limit(3):
            print(f"   • {app.get('item_id')} - Status: {app.get('status')} - User: {app.get('user_id')}")
    
except Exception as e:
    print(f"   ❌ MongoDB Error: {e}")
    exit(1)

# Check files
print(f"\n6️⃣ Checking Project Files...")

files_to_check = {
    "templates/admin.html": ["tab-content-crud", "tab-content-subcategories", "Manage Services"],
    "static/admin.js": ["loadServicesList", "loadSubcategoryReport", "exportSubcategoryReportPDF"],
    "static/script.js": ["showMyApplications", "My Applications"],
    "app.py": ["get_all_items", "subcategory_report", "get_user_applications"]
}

issues = []

for file_path, keywords in files_to_check.items():
    print(f"\n   Checking {file_path}:")
    if not os.path.exists(file_path):
        print(f"      ❌ FILE NOT FOUND!")
        issues.append(f"{file_path} is missing")
        continue
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    missing = []
    for keyword in keywords:
        if keyword not in content:
            missing.append(keyword)
    
    if missing:
        print(f"      ❌ MISSING: {', '.join(missing)}")
        issues.append(f"{file_path} needs updating")
    else:
        print(f"      ✅ All required code present")

# Summary
print("\n" + "=" * 60)
print("📊 DIAGNOSTIC SUMMARY")
print("=" * 60)

if not issues and cat_count > 0:
    print("\n✅ ALL CHECKS PASSED!")
    print("\nYour system should be working. If not:")
    print("1. Make sure app is running: python app.py")
    print("2. Clear browser cache (Ctrl+Shift+Delete)")
    print("3. Check browser console for errors (F12)")
else:
    print("\n❌ ISSUES FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")
    
    if cat_count == 0:
        print(f"{len(issues)+1}. No data in database")
    
    print("\n🔧 TO FIX:")
    print("1. Download the latest files from the assistant")
    print("2. Replace the files listed above")
    print("3. Run: python mega_seed_15_categories.py")
    print("4. Restart: python app.py")

print("\n" + "=" * 60)