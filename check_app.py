"""
Quick Check - Is your app.py correct?
Run this to see if you have the right version
"""

import os

print("🔍 Checking your app.py file...\n")

if not os.path.exists("app.py"):
    print("❌ app.py NOT FOUND in current directory!")
    print("   Make sure you're in the project folder")
    exit(1)

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Critical checks
checks = {
    'Admin route exists': '@app.route("/admin")' in content,
    'Admin login function': 'def admin_login()' in content,
    'Render admin template': 'render_template("admin.html")' in content,
    'CRUD endpoints': 'def get_all_items()' in content,
    'Application save': 'def submit_application(' in content,
    'User applications': 'def get_user_applications(' in content,
}

print("Required Features:")
print("-" * 40)
all_good = True
for feature, exists in checks.items():
    status = "✅" if exists else "❌"
    print(f"{status} {feature}")
    if not exists:
        all_good = False

print("-" * 40)

if all_good:
    print("\n✅ Your app.py looks correct!")
    print("\nIf /admin still shows error:")
    print("1. Stop the app (Ctrl+C)")
    print("2. Restart: python app.py")
    print("3. Check for errors in terminal")
else:
    print("\n❌ Your app.py is MISSING features!")
    print("\n🔧 FIX: Replace with the app.py from the assistant")
    print("   The file should be ~40KB with all endpoints")

# File size check
size = os.path.getsize("app.py")
print(f"\nFile size: {size:,} bytes")
if size < 30000:
    print("⚠️  WARNING: File is too small!")
    print("   Expected: ~40,000-45,000 bytes")
    print("   You likely have an old version")
elif size > 30000:
    print("✅ File size looks good")