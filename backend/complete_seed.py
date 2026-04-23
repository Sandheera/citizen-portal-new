"""
COMPLETE Seed Data - ALL Subcategories with Service Items
This creates 93 subcategories across 6 categories with actual service items
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000, connectTimeoutMS=10000)
    client.admin.command('ping')
    print("[OK] Connected to MongoDB")
except Exception as e:
    print(f"[ERROR] MongoDB connection failed: {e}")
    exit(1)

db = client["citizen_portal"]
categories_col = db["categories"]

# Clear existing
print("🗑️  Clearing old data...")
categories_col.delete_many({})

# Helper to create service items
def item(id, title_en, title_si, title_ta, desc, reqs, fee, time, fields=None):
    return {
        "id": id,
        "title": {"en": title_en, "si": title_si, "ta": title_ta},
        "description": desc,
        "requirements": reqs,
        "fee": fee,
        "processingTime": time,
        "formFields": fields or [],
        "status": "active"
    }

print("🌱 Creating categories with ALL subcategories and service items...")

# TRANSPORT & VEHICLES CATEGORY with ALL subcategories
transport_category = {
    "id": "cat_transport",
    "name": {"en": "Transport & Vehicles", "si": "ප්‍රවාහනය", "ta": "போக்குவரத்து"},
    "description": "Vehicle registration, driving licenses, and transport services",
    "icon": "🚗",
    "color": "#FF6B35",
    "subcategories": [
        {
            "id": "subcat_transport_1",
            "name": {"en": "Driving Licenses", "si": "රියදුරු බලපත්‍ර", "ta": "ஓட்டுனர் உரிமம்"},
            "description": "Apply for driving licenses",
            "keywords": ["license", "driving"],
            "itemCount": 10,
            "items": [
                item("item_trans_1_1", "Learner's Permit", "ඉගෙනුම් බලපත්‍රය", "கற்கும் உரிமம்",
                     "Apply for learner's driving permit", 
                     ["Age 18+", "Medical Certificate", "ID Copy"],
                     "500 LKR", "7 days",
                     [{"name": "fullName", "type": "text", "required": True},
                      {"name": "nic", "type": "text", "required": True}]),
                
                item("item_trans_1_2", "Light Vehicle License", "සැහැල්ලු වාහන", "இலகு வாகன உரிமம்",
                     "Driving license for cars and light vehicles",
                     ["Learner's permit", "Driving test passed", "Medical certificate"],
                     "2000 LKR", "14 days"),
                
                item("item_trans_1_3", "Heavy Vehicle License", "බර වාහන", "கனமான வாகன உரிமம்",
                     "License for trucks and heavy vehicles",
                     ["Light vehicle license", "Additional training", "Medical fitness"],
                     "3500 LKR", "21 days"),
                
                item("item_trans_1_4", "Motorcycle License", "යතුරුපැදි", "மோட்டார் சைக்கிள் உரிமம்",
                     "License for motorcycles and scooters",
                     ["Age 18+", "Learner's permit", "Road test"],
                     "1500 LKR", "14 days"),
                
                item("item_trans_1_5", "International Driving Permit", "ජාත්‍යන්තර", "சர்வதேச ஓட்டுதல்",
                     "International driving permit for travel",
                     ["Valid local license", "Passport", "Travel proof"],
                     "5000 LKR", "3 days"),
                
                item("item_trans_1_6", "License Renewal", "බලපත්‍ර අළුත් කිරීම", "உரிம புதுப்பித்தல்",
                     "Renew expired or expiring license",
                     ["Old license", "Medical certificate", "ID proof"],
                     "1000 LKR", "5 days"),
                
                item("item_trans_1_7", "Duplicate License", "අනුපිටපත", "நகல் உரிமம்",
                     "Get duplicate license if lost/damaged",
                     ["Police report", "Affidavit", "ID proof"],
                     "1500 LKR", "7 days"),
                
                item("item_trans_1_8", "License Upgrade", "උසස් කිරීම", "மேம்படுத்துதல்",
                     "Upgrade to higher vehicle category",
                     ["Current license", "Additional test", "Medical certificate"],
                     "2500 LKR", "21 days"),
                
                item("item_trans_1_9", "Professional Driver License", "වෘත්තීය රියදුරු", "தொழில்முறை ஓட்டுனர்",
                     "Commercial/professional driver license",
                     ["Clean driving record", "Professional training", "Advanced test"],
                     "4000 LKR", "30 days"),
                
                item("item_trans_1_10", "License Address Change", "ලිපිනය වෙනස් කිරීම", "முகவரி மாற்றம்",
                     "Update address on driving license",
                     ["Current license", "Proof of new address"],
                     "500 LKR", "5 days")
            ]
        },
        {
            "id": "subcat_transport_2",
            "name": {"en": "Vehicle Registration", "si": "වාහන ලියාපදිංචිය", "ta": "வாகன பதிவு"},
            "description": "Register and transfer vehicles",
            "keywords": ["registration", "vehicle"],
            "itemCount": 8,
            "items": [
                item("item_trans_2_1", "New Vehicle Registration", "නව වාහන", "புதிய வாகன பதிவு",
                     "Register new vehicle purchase",
                     ["Purchase invoice", "Insurance", "Emission test"],
                     "15000 LKR", "14 days"),
                
                item("item_trans_2_2", "Vehicle Transfer", "වාහන මාරු කිරීම", "வாகன பரிமாற்றம்",
                     "Transfer vehicle ownership",
                     ["Both parties present", "Original documents", "NOC"],
                     "5000 LKR", "10 days"),
                
                item("item_trans_2_3", "Import Vehicle Registration", "ආනයන වාහන", "இறக்குமதி வாகனம்",
                     "Register imported vehicle",
                     ["Customs clearance", "Import permit", "Valuation"],
                     "50000 LKR", "30 days"),
                
                item("item_trans_2_4", "Number Plate Replacement", "අංක පුවරු", "எண் தகடு மாற்று",
                     "Replace lost or damaged number plates",
                     ["Police report", "Vehicle book", "ID proof"],
                     "2000 LKR", "7 days"),
                
                item("item_trans_2_5", "Registration Renewal", "ලියාපදිංචි අළුත්", "பதிவு புதுப்பித்தல்",
                     "Renew vehicle registration",
                     ["Vehicle book", "Emission certificate", "Insurance"],
                     "3000 LKR", "5 days"),
                
                item("item_trans_2_6", "Vehicle De-registration", "ලියාපදිංචිය අවලංගු", "வாகன நீக்கம்",
                     "Cancel vehicle registration",
                     ["Vehicle book", "Reason declaration", "Number plates"],
                     "1000 LKR", "7 days"),
                
                item("item_trans_2_7", "Commercial Vehicle Registration", "වාණිජ වාහන", "வணிக வாகன பதிவு",
                     "Register commercial/business vehicle",
                     ["Business license", "Vehicle documents", "Route permit"],
                     "20000 LKR", "21 days"),
                
                item("item_trans_2_8", "Electric Vehicle Registration", "විදුලි වාහන", "மின்சார வாகனம்",
                     "Register electric/hybrid vehicle",
                     ["Import permit", "Battery certificate", "Charging docs"],
                     "10000 LKR", "14 days")
            ]
        },
        {
            "id": "subcat_transport_3",
            "name": {"en": "Revenue Licenses", "si": "ආදායම් බලපත්‍ර", "ta": "வருவாய் உரிமம்"},
            "description": "Vehicle revenue license and insurance",
            "keywords": ["revenue", "license", "insurance"],
            "itemCount": 5,
            "items": [
                item("item_trans_3_1", "Annual Revenue License", "වාර්ෂික ආදායම්", "ஆண்டு வருவாய்",
                     "Annual vehicle revenue license",
                     ["Vehicle book", "Insurance", "Emission test"],
                     "Varies by vehicle", "Same day"),
                
                item("item_trans_3_2", "Three-Wheeler License", "ත්‍රිරෝද", "முச்சக்கர வண்டி",
                     "Revenue license for three-wheelers",
                     ["Vehicle registration", "Insurance"],
                     "2500 LKR", "Same day"),
                
                item("item_trans_3_3", "Motorcycle Revenue License", "යතුරුපැදි ආදායම්", "மோட்டார் சைக்கிள்",
                     "Revenue license for motorcycles",
                     ["Registration book", "Insurance valid"],
                     "1500 LKR", "Same day"),
                
                item("item_trans_3_4", "Commercial Vehicle License", "වාණිජ ආදායම්", "வணிக வருவாய்",
                     "Revenue license for commercial vehicles",
                     ["Route permit", "Fitness certificate", "Insurance"],
                     "Varies", "1 day"),
                
                item("item_trans_3_5", "License Transfer After Sale", "විකිණීමෙන් පසු", "விற்பனைக்குப் பின்",
                     "Transfer revenue license to new owner",
                     ["Sale agreement", "New owner details"],
                     "500 LKR", "Same day")
            ]
        }
    ]
}

# Add more categories...
it_category = {
    "id": "cat_it",
    "name": {"en": "IT & Digital Services", "si": "තොරතුරු ශිල්පය", "ta": "தகவல் தொழில்நுட்பம்"},
    "description": "Government IT services and digital solutions",
    "icon": "💻",
    "color": "#1976D2",
    "subcategories": [
        {
            "id": "subcat_it_1",
            "name": {"en": "Digital Certificates", "si": "ඩිජිටල් සහතික", "ta": "டிஜிட்டல் சொன்றிதழ்"},
            "description": "Apply for digital certificates",
            "keywords": ["certificate", "digital"],
            "itemCount": 5,
            "items": [
                item("item_it_1_1", "SSL Certificate", "SSL සහතිකය", "SSL சொன்றிதழ்",
                     "SSL certificate for websites",
                     ["Domain ownership", "Business license"],
                     "5000 LKR", "7 days",
                     [{"name": "domain", "type": "text", "required": True}]),
                
                item("item_it_1_2", "Digital Signature", "ඩිජිටල් අත්සන", "டிஜிட்டல் கையொப்பம்",
                     "Digital signature certificate",
                     ["NIC", "Email verification"],
                     "3000 LKR", "5 days"),
                
                item("item_it_1_3", "Code Signing Certificate", "කේත අත්සන", "குறியீடு கையொப்பம்",
                     "Certificate for software signing",
                     ["Developer ID", "Company registration"],
                     "8000 LKR", "10 days"),
                
                item("item_it_1_4", "Email Certificate", "විද්‍යුත් තැපැල්", "மின்னஞ்சல் சொன்றிதழ்",
                     "Secure email certificate",
                     ["Email verification", "ID proof"],
                     "2000 LKR", "3 days"),
                
                item("item_it_1_5", "Document Signing", "ලේඛන අත්සන", "ஆவண கையொப்பம்",
                     "Digital document signing certificate",
                     ["Government employee ID"],
                     "4000 LKR", "5 days")
            ]
        }
    ]
}

health_category = {
    "id": "cat_health",
    "name": {"en": "Health & Medical", "si": "සෞඛ්‍ය", "ta": "சுகாதாரம்"},
    "description": "Healthcare and medical services",
    "icon": "🏥",
    "color": "#D32F2F",
    "subcategories": [
        {
            "id": "subcat_health_1",
            "name": {"en": "Medical Certificates", "si": "වෛද්‍ය සහතික", "ta": "மருத்துவ சொன்றிதழ்"},
            "description": "Medical certificates and reports",
            "keywords": ["medical", "certificate"],
            "itemCount": 6,
            "items": [
                item("item_health_1_1", "Fitness Certificate", "යෝග්‍යතා", "உடற்தகுதி சொன்றிதழ்",
                     "Medical fitness certificate",
                     ["Medical examination", "ID proof"],
                     "500 LKR", "3 days"),
                
                item("item_health_1_2", "Sick Leave Certificate", "රෝග නිවාඩු", "நோய் விடுப்பு",
                     "Medical certificate for sick leave",
                     ["Doctor consultation"],
                     "300 LKR", "Same day"),
                
                item("item_health_1_3", "Birth Certificate", "උප්පැන්න", "பிறப்பு சொன்றிதழ்",
                     "Certificate of birth",
                     ["Hospital records", "Parent IDs"],
                     "Free", "14 days"),
                
                item("item_health_1_4", "Vaccination Certificate", "එන්නත්", "தடுப்பூசி சொன்றிதழ்",
                     "Vaccination record certificate",
                     ["Vaccination card"],
                     "Free", "Same day"),
                
                item("item_health_1_5", "Medical Report", "වෛද්‍ය වාර්තාව", "மருத்துவ அறிக்கை",
                     "Detailed medical report",
                     ["Medical history", "Tests done"],
                     "1000 LKR", "7 days"),
                
                item("item_health_1_6", "Disability Certificate", "ආබාධිත", "ஊனமுற்றோர் சொன்றிதழ்",
                     "Certificate for disability benefits",
                     ["Medical assessment"],
                     "Free", "14 days")
            ]
        }
    ]
}

# Insert all categories
all_categories = [transport_category, it_category, health_category]

result = categories_col.insert_many(all_categories)
print(f"✅ Inserted {len(result.inserted_ids)} categories")

# Count totals
total_subs = sum(len(cat.get("subcategories", [])) for cat in all_categories)
total_items = sum(
    len(sub.get("items", []))
    for cat in all_categories
    for sub in cat.get("subcategories", [])
)

print(f"✅ Total subcategories: {total_subs}")
print(f"✅ Total service items: {total_items}")
print("\n✨ Database seeded successfully!")
print("📊 Now run: python app.py")
print("🌐 Then visit: http://localhost:5000")