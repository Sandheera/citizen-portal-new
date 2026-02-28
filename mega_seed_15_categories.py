"""
MEGA SEED FILE - 15 Categories × 15 Subcategories × 12 Services = 2700 Services
Complete working seed with all categories fully populated
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000, connectTimeoutMS=10000)
    client.admin.command('ping')
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    exit(1)

db = client["citizen_portal"]
categories_col = db["categories"]

print("🗑️  Clearing old data...")
categories_col.delete_many({})

# Helper to create service items
def make_items(cat_prefix, sub_num, sub_name_en, count=12):
    """Generate realistic service items"""
    items = []
    
    # Service templates - 12 types
    templates = [
        ("New Application", "නව අයදුම්පත", "புதிய விண்ணப்பம்", "Apply for new {service}", ["ID Copy", "Photo", "Application Fee"], "1000 LKR", "7-10 days"),
        ("Renewal Service", "අළුත් කිරීම", "புதுப்பித்தல்", "Renew your {service}", ["Current Certificate", "Payment Receipt"], "500 LKR", "3-5 days"),
        ("Duplicate Certificate", "අනුපිටපත්", "நகல் சொன்றிதழ்", "Get duplicate copy of {service}", ["Police Report", "Affidavit", "ID"], "750 LKR", "5 days"),
        ("Amendment Request", "සංශෝධනය", "திருத்தம்", "Modify details in {service}", ["Original Document", "Proof of Change"], "600 LKR", "3-5 days"),
        ("Transfer Service", "මාරු", "பரிமாற்றம்", "Transfer {service} to another party", ["Both Parties Present", "NOC", "Transfer Fee"], "1200 LKR", "10-14 days"),
        ("Cancellation", "අවලංගු", "ரத்து", "Cancel existing {service}", ["Original Certificate", "Cancellation Letter"], "300 LKR", "2-3 days"),
        ("Verification", "සත්‍යාපනය", "சரிபார்த்தல்", "Verify authenticity of {service}", ["Document Copy"], "400 LKR", "1-2 days"),
        ("Express Processing", "ඉක්මන්", "விரைவு", "Fast-track {service} processing", ["All Regular Docs", "Express Fee"], "2500 LKR", "24-48 hours"),
        ("Online Submission", "අන්තර්ජාල", "ஆன்லைன்", "Submit {service} application online", ["Digital Docs", "Email"], "900 LKR", "5-7 days"),
        ("Status Inquiry", "තත්ත්වය", "நிலை", "Check status of {service} application", ["Application Number"], "Free", "Immediate"),
        ("Complaint Filing", "පැමිණිලි", "புகார்", "File complaint regarding {service}", ["Details", "Supporting Docs"], "Free", "3-5 days"),
        ("Information Request", "තොරතුරු", "தகவல்", "Request information about {service}", ["ID Proof"], "Free", "1-2 days")
    ]
    
    for i in range(count):
        template = templates[i]
        items.append({
            "id": f"{cat_prefix}_{sub_num}_{i+1}",
            "title": {
                "en": f"{template[0]} - {sub_name_en}",
                "si": f"{template[1]} - {sub_name_en}",
                "ta": f"{template[2]} - {sub_name_en}"
            },
            "description": template[3].format(service=sub_name_en.lower()),
            "requirements": template[4],
            "fee": template[5],
            "processingTime": template[6],
            "formFields": [
                {"name": "fullName", "type": "text", "required": True, "label": "Full Name"},
                {"name": "nic", "type": "text", "required": True, "label": "NIC Number"},
                {"name": "contactNumber", "type": "tel", "required": True, "label": "Contact Number"},
                {"name": "email", "type": "email", "required": True, "label": "Email Address"},
                {"name": "address", "type": "text", "required": False, "label": "Address"}
            ],
            "status": "active"
        })
    return items

print("🌱 Creating 15 MEGA categories...")

# Define all 15 categories with complete subcategories
all_categories = []

# Category templates with 15 subcategories each
category_templates = [
    {
        "id": "cat_it",
        "name": {"en": "IT & Digital Services", "si": "තොරතුරු තාක්ෂණය", "ta": "தகவல் தொழில்நுட்பம்"},
        "icon": "💻", "color": "#1976D2",
        "subcategories": [
            ("Digital Certificates", ["certificate", "ssl", "digital"]),
            ("Software Development", ["software", "development", "coding"]),
            ("Cloud Services", ["cloud", "hosting", "server"]),
            ("Cybersecurity", ["security", "protection", "firewall"]),
            ("IT Training Programs", ["training", "course", "learning"]),
            ("Technical Support", ["support", "help", "troubleshoot"]),
            ("Web Development", ["website", "web", "design"]),
            ("Mobile Applications", ["mobile", "app", "android"]),
            ("Data Analytics", ["data", "analytics", "insights"]),
            ("Network Infrastructure", ["network", "lan", "infrastructure"]),
            ("Database Services", ["database", "sql", "storage"]),
            ("DevOps Solutions", ["devops", "automation", "ci/cd"]),
            ("AI & Machine Learning", ["ai", "ml", "automation"]),
            ("Hardware Support", ["hardware", "repair", "maintenance"]),
            ("IT Consulting", ["consulting", "advisory", "strategy"])
        ]
    },
    {
        "id": "cat_health",
        "name": {"en": "Health & Medical", "si": "සෞඛ්‍ය සේවා", "ta": "சுகாதார சேவைகள்"},
        "icon": "🏥", "color": "#D32F2F",
        "subcategories": [
            ("Medical Certificates", ["medical", "certificate", "health"]),
            ("Vaccination Services", ["vaccine", "immunization", "shot"]),
            ("Hospital Admissions", ["hospital", "admission", "emergency"]),
            ("Pharmacy Services", ["pharmacy", "medicine", "prescription"]),
            ("Mental Health Services", ["mental", "counseling", "therapy"]),
            ("Dental Services", ["dental", "teeth", "oral"]),
            ("Eye Care Services", ["eye", "vision", "optical"]),
            ("Maternity Services", ["maternity", "pregnancy", "delivery"]),
            ("Child Healthcare", ["child", "pediatric", "baby"]),
            ("Elderly Care", ["elderly", "senior", "geriatric"]),
            ("Emergency Services", ["emergency", "ambulance", "urgent"]),
            ("Laboratory Tests", ["lab", "test", "diagnosis"]),
            ("Health Insurance", ["insurance", "coverage", "medical"]),
            ("Medical Records", ["records", "history", "reports"]),
            ("Telemedicine", ["telemedicine", "online", "virtual"])
        ]
    },
    {
        "id": "cat_education",
        "name": {"en": "Education & Learning", "si": "අධ්‍යාපන සේවා", "ta": "கல்வி சேவைகள்"},
        "icon": "📚", "color": "#4CAF50",
        "subcategories": [
            ("School Admissions", ["school", "admission", "enrollment"]),
            ("University Applications", ["university", "college", "higher"]),
            ("Scholarship Programs", ["scholarship", "grant", "financial"]),
            ("Online Courses", ["online", "elearning", "digital"]),
            ("Vocational Training", ["vocational", "skills", "technical"]),
            ("Language Programs", ["language", "english", "foreign"]),
            ("Exam Registration", ["exam", "test", "assessment"]),
            ("Certificate Programs", ["certificate", "diploma", "course"]),
            ("Student Loans", ["loan", "financing", "education"]),
            ("Study Materials", ["books", "materials", "resources"]),
            ("Tutoring Services", ["tutor", "coaching", "classes"]),
            ("Distance Learning", ["distance", "correspondence", "remote"]),
            ("Special Education", ["special", "disability", "inclusive"]),
            ("Adult Education", ["adult", "continuing", "professional"]),
            ("Career Counseling", ["career", "guidance", "counseling"])
        ]
    },
    {
        "id": "cat_transport",
        "name": {"en": "Transport & Vehicles", "si": "ප්‍රවාහන සේවා", "ta": "போக்குவரத்து சேவைகள்"},
        "icon": "🚗", "color": "#FF6B35",
        "subcategories": [
            ("Driving Licenses", ["license", "driving", "permit"]),
            ("Vehicle Registration", ["registration", "vehicle", "new"]),
            ("Revenue Licenses", ["revenue", "annual", "tax"]),
            ("Vehicle Insurance", ["insurance", "vehicle", "coverage"]),
            ("Parking Permits", ["parking", "permit", "zone"]),
            ("Route Permits", ["route", "commercial", "transport"]),
            ("Vehicle Inspection", ["inspection", "emission", "test"]),
            ("Traffic Violations", ["fine", "violation", "penalty"]),
            ("Public Transport", ["bus", "train", "public"]),
            ("Taxi Services", ["taxi", "cab", "ride"]),
            ("Vehicle Transfer", ["transfer", "ownership", "sale"]),
            ("Import Permits", ["import", "customs", "foreign"]),
            ("Emission Testing", ["emission", "pollution", "test"]),
            ("Road Tax Payments", ["tax", "road", "payment"]),
            ("Vehicle Modifications", ["modification", "custom", "upgrade"])
        ]
    },
    {
        "id": "cat_land",
        "name": {"en": "Land & Housing", "si": "ඉඩම් හා නිවාස", "ta": "நில மற்றும் வீடு"},
        "icon": "🏘️", "color": "#795548",
        "subcategories": [
            ("Property Deeds", ["deed", "property", "ownership"]),
            ("Building Permits", ["building", "construction", "permit"]),
            ("Land Surveys", ["survey", "land", "measurement"]),
            ("Property Tax", ["tax", "property", "assessment"]),
            ("Construction Approvals", ["approval", "construction", "plan"]),
            ("Housing Loans", ["loan", "housing", "mortgage"]),
            ("Rental Agreements", ["rental", "lease", "agreement"]),
            ("Land Registration", ["registration", "land", "title"]),
            ("Property Transfers", ["transfer", "property", "sale"]),
            ("Utility Connections", ["utility", "water", "electricity"]),
            ("Property Valuation", ["valuation", "appraisal", "value"]),
            ("Zoning Permits", ["zoning", "permit", "residential"]),
            ("Renovation Permits", ["renovation", "remodel", "alteration"]),
            ("Land Development", ["development", "subdivision", "planning"]),
            ("Property Insurance", ["insurance", "property", "protection"])
        ]
    },
    # Add 10 more categories...
    {
        "id": "cat_elections",
        "name": {"en": "Elections & Voting", "si": "මැතිවරණ සේවා", "ta": "தேர்தல் சேவைகள்"},
        "icon": "🗳️", "color": "#9C27B0",
        "subcategories": [
            ("Voter Registration", ["voter", "registration", "id"]),
            ("Candidate Nomination", ["candidate", "nomination", "election"]),
            ("Election Results", ["results", "outcome", "votes"]),
            ("Polling Information", ["polling", "station", "location"]),
            ("Absentee Voting", ["absentee", "postal", "vote"]),
            ("Voter ID Cards", ["id", "card", "voter"]),
            ("Election Complaints", ["complaint", "violation", "report"]),
            ("Party Registration", ["party", "political", "registration"]),
            ("Campaign Permits", ["campaign", "permit", "rally"]),
            ("Observer Applications", ["observer", "monitor", "watch"]),
            ("Electoral Roll", ["roll", "list", "voters"]),
            ("Referendum Services", ["referendum", "vote", "public"]),
            ("Local Elections", ["local", "municipal", "council"]),
            ("Election Training", ["training", "staff", "official"]),
            ("Vote Counting", ["counting", "tally", "results"])
        ]
    },
    {
        "id": "cat_business",
        "name": {"en": "Business & Commerce", "si": "ව්‍යාපාර සේවා", "ta": "வணிக சேவைகள்"},
        "icon": "💼", "color": "#FF9800",
        "subcategories": [
            ("Business Registration", ["business", "registration", "company"]),
            ("Trade Licenses", ["trade", "license", "permit"]),
            ("Company Formation", ["company", "incorporation", "formation"]),
            ("Tax Registration", ["tax", "registration", "tin"]),
            ("Import/Export Licenses", ["import", "export", "trade"]),
            ("Professional Licenses", ["professional", "license", "certification"]),
            ("Patent Services", ["patent", "intellectual", "property"]),
            ("Trademark Registration", ["trademark", "brand", "logo"]),
            ("Copyright Services", ["copyright", "protection", "rights"]),
            ("Business Permits", ["permit", "business", "operation"]),
            ("Food Licenses", ["food", "restaurant", "safety"]),
            ("Liquor Licenses", ["liquor", "alcohol", "permit"]),
            ("Entertainment Licenses", ["entertainment", "venue", "event"]),
            ("Industrial Permits", ["industrial", "factory", "manufacturing"]),
            ("Business Insurance", ["insurance", "business", "coverage"])
        ]
    },
    {
        "id": "cat_finance",
        "name": {"en": "Finance & Taxation", "si": "මූල්‍ය සේවා", "ta": "நிதி சேவைகள்"},
        "icon": "💰", "color": "#4CAF50",
        "subcategories": [
            ("Income Tax Returns", ["income", "tax", "return"]),
            ("Corporate Tax", ["corporate", "tax", "business"]),
            ("VAT Registration", ["vat", "tax", "registration"]),
            ("Tax Clearance", ["clearance", "tax", "certificate"]),
            ("Customs Duty", ["customs", "duty", "import"]),
            ("Property Tax", ["property", "tax", "land"]),
            ("Stamp Duty", ["stamp", "duty", "legal"]),
            ("Tax Appeals", ["appeal", "dispute", "objection"]),
            ("Tax Refunds", ["refund", "rebate", "return"]),
            ("Audit Services", ["audit", "financial", "review"]),
            ("Financial Planning", ["planning", "investment", "wealth"]),
            ("Loan Applications", ["loan", "credit", "financing"]),
            ("Banking Services", ["banking", "account", "services"]),
            ("Investment Services", ["investment", "stocks", "bonds"]),
            ("Insurance Claims", ["insurance", "claim", "settlement"])
        ]
    },
    {
        "id": "cat_agriculture",
        "name": {"en": "Agriculture & Farming", "si": "කෘෂිකර්ම සේවා", "ta": "விவசாய சேவைகள்"},
        "icon": "🌾", "color": "#8BC34A",
        "subcategories": [
            ("Farming Licenses", ["farming", "agriculture", "license"]),
            ("Agricultural Subsidies", ["subsidy", "grant", "support"]),
            ("Crop Insurance", ["insurance", "crop", "protection"]),
            ("Land Allocation", ["land", "allocation", "farming"]),
            ("Irrigation Services", ["irrigation", "water", "system"]),
            ("Fertilizer Distribution", ["fertilizer", "subsidy", "farming"]),
            ("Seed Supply", ["seed", "distribution", "crops"]),
            ("Livestock Registration", ["livestock", "animal", "registration"]),
            ("Agricultural Loans", ["loan", "farming", "credit"]),
            ("Market Access", ["market", "selling", "produce"]),
            ("Cold Storage", ["storage", "cold", "preservation"]),
            ("Farm Equipment", ["equipment", "machinery", "tools"]),
            ("Organic Certification", ["organic", "certification", "natural"]),
            ("Agricultural Training", ["training", "farming", "education"]),
            ("Pest Control", ["pest", "control", "protection"])
        ]
    },
    {
        "id": "cat_police",
        "name": {"en": "Police & Security", "si": "පොලිස් සේවා", "ta": "காவல் சேவைகள்"},
        "icon": "👮", "color": "#2196F3",
        "subcategories": [
            ("Police Clearance", ["clearance", "police", "certificate"]),
            ("Lost & Found", ["lost", "found", "property"]),
            ("Crime Reporting", ["crime", "report", "complaint"]),
            ("Security Licenses", ["security", "license", "guard"]),
            ("Firearms Licenses", ["firearm", "gun", "weapon"]),
            ("Background Checks", ["background", "check", "verification"]),
            ("Character Certificates", ["character", "certificate", "reference"]),
            ("Travel Clearance", ["travel", "clearance", "emigration"]),
            ("Complaint Registration", ["complaint", "fir", "report"]),
            ("Witness Protection", ["witness", "protection", "safety"]),
            ("Victim Support", ["victim", "support", "assistance"]),
            ("Community Policing", ["community", "policing", "safety"]),
            ("Cybercrime Reporting", ["cybercrime", "online", "fraud"]),
            ("Traffic Reports", ["traffic", "accident", "report"]),
            ("Security Systems", ["security", "alarm", "cctv"])
        ]
    },
    {
        "id": "cat_welfare",
        "name": {"en": "Social Welfare", "si": "සමාජ සුබසාධන", "ta": "சமூக நல சேவைகள்"},
        "icon": "🤝", "color": "#E91E63",
        "subcategories": [
            ("Social Benefits", ["benefit", "welfare", "assistance"]),
            ("Disability Support", ["disability", "support", "aid"]),
            ("Elderly Care Programs", ["elderly", "senior", "care"]),
            ("Child Welfare", ["child", "welfare", "protection"]),
            ("Housing Assistance", ["housing", "assistance", "shelter"]),
            ("Food Assistance", ["food", "meals", "nutrition"]),
            ("Cash Transfers", ["cash", "transfer", "payment"]),
            ("Pension Services", ["pension", "retirement", "benefits"]),
            ("Healthcare Subsidies", ["healthcare", "subsidy", "medical"]),
            ("Education Grants", ["education", "grant", "scholarship"]),
            ("Emergency Relief", ["emergency", "relief", "disaster"]),
            ("Unemployment Benefits", ["unemployment", "benefit", "job"]),
            ("Women's Services", ["women", "support", "empowerment"]),
            ("Youth Programs", ["youth", "program", "development"]),
            ("Community Services", ["community", "service", "support"])
        ]
    },
    {
        "id": "cat_tourism",
        "name": {"en": "Tourism & Travel", "si": "සංචාරක සේවා", "ta": "சுற்றுலா சேவைகள்"},
        "icon": "✈️", "color": "#00BCD4",
        "subcategories": [
            ("Visa Applications", ["visa", "travel", "entry"]),
            ("Passport Services", ["passport", "travel", "document"]),
            ("Travel Permits", ["permit", "travel", "authorization"]),
            ("Tour Guide Licenses", ["guide", "tour", "license"]),
            ("Hotel Registration", ["hotel", "accommodation", "registration"]),
            ("Tourism Permits", ["tourism", "permit", "business"]),
            ("Travel Insurance", ["insurance", "travel", "coverage"]),
            ("Currency Exchange", ["currency", "exchange", "forex"]),
            ("Travel Information", ["information", "travel", "guide"]),
            ("National Parks", ["park", "national", "wildlife"]),
            ("Beach Permits", ["beach", "permit", "access"]),
            ("Adventure Sports", ["adventure", "sports", "activity"]),
            ("Cultural Sites", ["cultural", "heritage", "monument"]),
            ("Event Permits", ["event", "festival", "permit"]),
            ("Tourist Complaints", ["complaint", "tourist", "feedback"])
        ]
    },
    {
        "id": "cat_environment",
        "name": {"en": "Environment & Energy", "si": "පරිසර සේවා", "ta": "சுற்றுச்சூழல் சேவைகள்"},
        "icon": "🌍", "color": "#4CAF50",
        "subcategories": [
            ("Environmental Permits", ["environment", "permit", "clearance"]),
            ("Waste Management", ["waste", "disposal", "recycling"]),
            ("Pollution Control", ["pollution", "control", "emission"]),
            ("Tree Planting", ["tree", "planting", "green"]),
            ("Solar Energy", ["solar", "energy", "renewable"]),
            ("Water Conservation", ["water", "conservation", "save"]),
            ("Green Building", ["green", "building", "sustainable"]),
            ("Climate Programs", ["climate", "carbon", "reduction"]),
            ("Wildlife Protection", ["wildlife", "protection", "conservation"]),
            ("Recycling Services", ["recycling", "waste", "reuse"]),
            ("Energy Audits", ["energy", "audit", "efficiency"]),
            ("Environmental Impact", ["impact", "assessment", "study"]),
            ("Coastal Protection", ["coastal", "beach", "erosion"]),
            ("Air Quality", ["air", "quality", "monitoring"]),
            ("Eco-Certification", ["eco", "certification", "green"])
        ]
    },
    {
        "id": "cat_legal",
        "name": {"en": "Legal & Judicial", "si": "නීති සේවා", "ta": "சட்ட சேவைகள்"},
        "icon": "⚖️", "color": "#607D8B",
        "subcategories": [
            ("Court Cases", ["court", "case", "lawsuit"]),
            ("Legal Documentation", ["legal", "document", "contract"]),
            ("Notary Services", ["notary", "attestation", "certification"]),
            ("Marriage Registration", ["marriage", "registration", "certificate"]),
            ("Divorce Services", ["divorce", "separation", "legal"]),
            ("Will & Testament", ["will", "testament", "inheritance"]),
            ("Power of Attorney", ["power", "attorney", "authorization"]),
            ("Legal Aid", ["legal", "aid", "assistance"]),
            ("Birth Registration", ["birth", "registration", "certificate"]),
            ("Death Registration", ["death", "registration", "certificate"]),
            ("Name Change", ["name", "change", "legal"]),
            ("Adoption Services", ["adoption", "child", "legal"]),
            ("Mediation Services", ["mediation", "dispute", "resolution"]),
            ("Legal Consultation", ["consultation", "advice", "lawyer"]),
            ("Affidavit Services", ["affidavit", "sworn", "statement"])
        ]
    },
    {
        "id": "cat_labor",
        "name": {"en": "Labor & Employment", "si": "කම්කරු සේවා", "ta": "தொழிலாளர் சேவைகள்"},
        "icon": "👷", "color": "#FF5722",
        "subcategories": [
            ("Job Registration", ["job", "employment", "registration"]),
            ("Employment Contracts", ["contract", "employment", "agreement"]),
            ("Work Permits", ["permit", "work", "authorization"]),
            ("Labor Complaints", ["complaint", "labor", "dispute"]),
            ("Unemployment Registration", ["unemployment", "registration", "benefit"]),
            ("Skills Training", ["training", "skills", "employment"]),
            ("Job Placement", ["placement", "job", "recruitment"]),
            ("Workplace Safety", ["safety", "workplace", "health"]),
            ("Employee Benefits", ["benefit", "employee", "welfare"]),
            ("Retirement Plans", ["retirement", "pension", "provident"]),
            ("Wage Disputes", ["wage", "salary", "dispute"]),
            ("Foreign Employment", ["foreign", "overseas", "work"]),
            ("Labor Laws", ["law", "labor", "rights"]),
            ("Trade Unions", ["union", "trade", "worker"]),
            ("Apprenticeships", ["apprentice", "training", "program"])
        ]
    }
]

# Create all categories
for cat_template in category_templates:
    category = {
        "id": cat_template["id"],
        "name": cat_template["name"],
        "description": f"Services related to {cat_template['name']['en'].lower()}",
        "icon": cat_template["icon"],
        "color": cat_template["color"],
        "subcategories": [
            {
                "id": f"sub_{cat_template['id'][4:]}_{i+1}",
                "name": {"en": sub[0], "si": sub[0], "ta": sub[0]},
                "description": f"Services related to {sub[0].lower()}",
                "keywords": sub[1],
                "itemCount": 12,
                "items": make_items(cat_template['id'][4:], i+1, sub[0], 12)
            }
            for i, sub in enumerate(cat_template["subcategories"])
        ]
    }
    all_categories.append(category)

print(f"📊 Inserting {len(all_categories)} categories...")
result = categories_col.insert_many(all_categories)

total_cats = len(all_categories)
total_subs = sum(len(cat.get("subcategories", [])) for cat in all_categories)
total_items = sum(len(sub.get("items", [])) for cat in all_categories for sub in cat.get("subcategories", []))

print(f"\n✅ SUCCESS!")
print(f"📁 Categories: {total_cats}")
print(f"📂 Subcategories: {total_subs}")
print(f"📄 Service Items: {total_items}")
print(f"\n🎉 Your system now has {total_items} services across {total_cats} categories!")
print(f"🚀 Run: python app.py")
print(f"🌐 Visit: http://localhost:5000")