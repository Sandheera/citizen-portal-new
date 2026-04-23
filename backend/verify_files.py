"""
Verification Script - Check if your files are up to date
Run this to see what's missing
"""

import os

print("🔍 Checking your project files...\n")

files_to_check = {
    "templates/admin.html": ["tab-content-crud", "tab-content-subcategories", "serviceModal"],
    "static/admin.js": ["loadSubcategoryReport", "loadServicesList", "exportSubcategoryReportPDF"],
    "app.py": ["get_subcategory_items", "add_service_item", "subcategory_report"]
}

for file_path, required_strings in files_to_check.items():
    print(f"📁 Checking: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"   ❌ File NOT FOUND!\n")
        continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    missing = []
    for req in required_strings:
        if req not in content:
            missing.append(req)
    
    if missing:
        print(f"   ❌ MISSING: {', '.join(missing)}")
        print(f"   → This file needs to be REPLACED!\n")
    else:
        print(f"   ✅ All required code present\n")

print("\n" + "="*50)
print("📊 SUMMARY:")
print("="*50)
print("\nIf you see ❌ above, you need to:")
print("1. Download the correct file from me")
print("2. Replace it in your project")
print("3. Restart your app")
print("\nFiles available from me:")
print("  - admin.html (for templates/)")
print("  - admin.js (for static/)")
print("  - app.py (for root folder)")