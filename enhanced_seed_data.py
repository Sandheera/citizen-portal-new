"""
Enhanced Seed Data with 15+ Subcategories for Each Category
Complete hierarchical data for public display
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
officers_col = db["officers"]
ads_col = db["ads"]

categories_col.delete_many({})
officers_col.delete_many({})
ads_col.delete_many({})

enhanced_categories = [
    {
        "id": "cat_it",
        "name": {"en": "IT & Digital Services", "si": "තොරතුරු ශිල්පය", "ta": "தகவல் தொழில்நுட்பம்"},
        "description": "Government IT services, digital certificates, and technology support",
        "icon": "💻",
        "color": "#1976D2",
        "subcategories": [
            {"id": "subcat_it_1", "name": {"en": "Digital Certificates", "si": "ඩිජිටල් සහතික", "ta": "டிஜிட்டல் சொன்றிதழ்"}, "description": "Apply for and manage digital certificates", "keywords": ["certificate", "digital", "authentication"], "itemCount": 5},
            {"id": "subcat_it_2", "name": {"en": "IT Training Programs", "si": "IT පුහුණු", "ta": "ஐடி பயிற்சி"}, "description": "Free and paid training courses", "keywords": ["training", "course", "programming"], "itemCount": 12},
            {"id": "subcat_it_3", "name": {"en": "Technical Support", "si": "තාක්ෂණ", "ta": "தொழில்நுட்ப"}, "description": "Get help with technical issues", "keywords": ["support", "help", "troubleshooting"], "itemCount": 8},
            {"id": "subcat_it_4", "name": {"en": "Web Development", "si": "වෙබ් සේවා", "ta": "வலை சேவைகள்"}, "description": "Government website development", "keywords": ["web", "development", "website"], "itemCount": 6},
            {"id": "subcat_it_5", "name": {"en": "Mobile Apps", "si": "මෝබයිල් යෙදුම්", "ta": "மொபைல் பயன்பாடு"}, "description": "Government mobile applications", "keywords": ["mobile", "app", "development"], "itemCount": 7},
            {"id": "subcat_it_6", "name": {"en": "Cybersecurity", "si": "සයිබර්", "ta": "சைபர் பாதுகாப்பு"}, "description": "Data protection and security", "keywords": ["security", "cyber", "protection"], "itemCount": 9},
            {"id": "subcat_it_7", "name": {"en": "Cloud Computing", "si": "මේघ", "ta": "கிளவுட் கணினி"}, "description": "Cloud infrastructure and services", "keywords": ["cloud", "computing", "infrastructure"], "itemCount": 8},
            {"id": "subcat_it_8", "name": {"en": "Data Analytics", "si": "දත්ත විශ්ලේෂණ", "ta": "தரவு பகுப்பாய்வு"}, "description": "Business intelligence and analytics", "keywords": ["data", "analytics", "intelligence"], "itemCount": 6},
            {"id": "subcat_it_9", "name": {"en": "AI Solutions", "si": "කෘත්‍රිම බුද්ධිමත්තාව", "ta": "செயற்கை நுண்ணறிவு"}, "description": "Artificial intelligence solutions", "keywords": ["AI", "machine learning", "automation"], "itemCount": 5},
            {"id": "subcat_it_10", "name": {"en": "Blockchain", "si": "බ්ලොකචේන්", "ta": "பிளாக்செயின்"}, "description": "Blockchain and distributed ledger", "keywords": ["blockchain", "ledger", "cryptocurrency"], "itemCount": 4},
            {"id": "subcat_it_11", "name": {"en": "IT Consulting", "si": "IT උපදෙස්", "ta": "ஐடி ஆலோசனை"}, "description": "Technology consulting and advisory", "keywords": ["consultancy", "advisory", "consulting"], "itemCount": 7},
            {"id": "subcat_it_12", "name": {"en": "System Administration", "si": "පද්ධති", "ta": "கணினி நிர்வாகம்"}, "description": "Server and network management", "keywords": ["system", "administration", "network"], "itemCount": 8},
            {"id": "subcat_it_13", "name": {"en": "Database Services", "si": "දත්ත සමුදාය", "ta": "தரவுத்தளம்"}, "description": "Database design and maintenance", "keywords": ["database", "SQL", "management"], "itemCount": 6},
            {"id": "subcat_it_14", "name": {"en": "IT Infrastructure", "si": "ඉතිරුව", "ta": "உள்கட்டமைப்பு"}, "description": "Complete IT infrastructure setup", "keywords": ["infrastructure", "hardware", "setup"], "itemCount": 9},
            {"id": "subcat_it_15", "name": {"en": "Software Testing", "si": "පරීක්ෂණ", "ta": "சோதனை"}, "description": "QA and software quality assurance", "keywords": ["testing", "QA", "quality"], "itemCount": 7},
            {"id": "subcat_it_16", "name": {"en": "Project Management", "si": "ව්‍යාපෘති", "ta": "திட්ட மேலாண்மை"}, "description": "IT project planning and execution", "keywords": ["project", "management", "planning"], "itemCount": 8}
        ]
    },
    {
        "id": "cat_health",
        "name": {"en": "Health & Medical", "si": "සෞඛ්‍ය සේවා", "ta": "சுகாதார சேவைகள්"},
        "description": "Healthcare, medical certificates, and wellness programs",
        "icon": "🏥",
        "color": "#D32F2F",
        "subcategories": [
            {"id": "subcat_health_1", "name": {"en": "Medical Certificates", "si": "වෛද්‍ය සහතික", "ta": "மருத்துவ சொன்றிதழ்"}, "description": "Apply for medical certificates", "keywords": ["medical", "certificate"], "itemCount": 7},
            {"id": "subcat_health_2", "name": {"en": "Vaccination", "si": "ශරීර ගතිකතා", "ta": "தடுப்பூசி"}, "description": "Immunization schedules", "keywords": ["vaccination", "vaccine"], "itemCount": 6},
            {"id": "subcat_health_3", "name": {"en": "Health Insurance", "si": "සෞඛ්‍ය රක්ෂණ", "ta": "சுகாதார காப்பீடு"}, "description": "Government insurance schemes", "keywords": ["insurance", "coverage"], "itemCount": 9},
            {"id": "subcat_health_4", "name": {"en": "Wellness Programs", "si": "සුබ දල", "ta": "ஆரோக்கிய திட்டங்கள்"}, "description": "Health promotion initiatives", "keywords": ["wellness", "prevention"], "itemCount": 5},
            {"id": "subcat_health_5", "name": {"en": "Disease Prevention", "si": "රෝග නිරෝධන", "ta": "நோய் தடுப்பு"}, "description": "Disease control programs", "keywords": ["disease", "prevention", "control"], "itemCount": 8},
            {"id": "subcat_health_6", "name": {"en": "Hospital Services", "si": "රෝහල් සේවා", "ta": "மருத்துவமனை"}, "description": "Hospital admission and procedures", "keywords": ["hospital", "admission", "service"], "itemCount": 10},
            {"id": "subcat_health_7", "name": {"en": "Emergency Care", "si": "හදිසි ප්‍රතිකාර", "ta": "அவசர சிகிச்சை"}, "description": "Emergency medical services", "keywords": ["emergency", "urgent", "care"], "itemCount": 6},
            {"id": "subcat_health_8", "name": {"en": "Maternal Care", "si": "මවුවතා සිටුවාවු", "ta": "தாய் சிகிச்சை"}, "description": "Pregnancy and childbirth services", "keywords": ["maternal", "pregnancy", "childbirth"], "itemCount": 7},
            {"id": "subcat_health_9", "name": {"en": "Child Health", "si": "ළමා සෞඛ්‍ය", "ta": "குழந்தை சுகாதாரம்"}, "description": "Pediatric and child health services", "keywords": ["child", "pediatric", "health"], "itemCount": 8},
            {"id": "subcat_health_10", "name": {"en": "Mental Health", "si": "මානසික සෞඛ්‍ය", "ta": "மனநல சேவை"}, "description": "Mental health and counseling", "keywords": ["mental", "psychology", "counseling"], "itemCount": 6},
            {"id": "subcat_health_11", "name": {"en": "Dental Care", "si": "දතු සිතුවාවු", "ta": "பல் சிகிச்சை"}, "description": "Dental health and treatment", "keywords": ["dental", "teeth", "care"], "itemCount": 5},
            {"id": "subcat_health_12", "name": {"en": "Eye Care", "si": "ඇසින් සිතුවාවු", "ta": "கண் சிகிச்சை"}, "description": "Ophthalmology services", "keywords": ["eye", "vision", "ophthalmology"], "itemCount": 5},
            {"id": "subcat_health_13", "name": {"en": "Pharmacy", "si": "ඖෂධ සපයාම", "ta": "மருந்து சேவைகள්"}, "description": "Prescription and medication services", "keywords": ["pharmacy", "medicine", "prescription"], "itemCount": 7},
            {"id": "subcat_health_14", "name": {"en": "Laboratory Tests", "si": "විද්‍යාගාර", "ta": "ஆய்வக சோதனைகள්"}, "description": "Medical laboratory services", "keywords": ["laboratory", "test", "diagnosis"], "itemCount": 9},
            {"id": "subcat_health_15", "name": {"en": "Physical Therapy", "si": "ශාරීරික ප්‍රතිකාර", "ta": "உடல் சிகிச்சை"}, "description": "Rehabilitation and therapy", "keywords": ["therapy", "rehabilitation", "physical"], "itemCount": 6},
            {"id": "subcat_health_16", "name": {"en": "Nutrition", "si": "පෝෂණ සेवा", "ta": "ஊட்டச்சத்து சேவைகள්"}, "description": "Nutritional counseling", "keywords": ["nutrition", "diet", "food"], "itemCount": 5}
        ]
    },
    {
        "id": "cat_education",
        "name": {"en": "Education & Learning", "si": "අධ්‍යාපනය", "ta": "கல்வி"},
        "description": "School enrollment, exam results, scholarships",
        "icon": "📚",
        "color": "#4CAF50",
        "subcategories": [
            {"id": "subcat_edu_1", "name": {"en": "School Enrollment", "si": "පාසල් ලිවුම්", "ta": "பள்ளி சேர்க்கை"}, "description": "Register for school admission", "keywords": ["school", "enrollment", "admission"], "itemCount": 8},
            {"id": "subcat_edu_2", "name": {"en": "Exam Results", "si": "විභාගයේ ප්‍රතිඵල", "ta": "தேர்வு முடிவுகள්"}, "description": "Check exam schedules and results", "keywords": ["exam", "results", "test"], "itemCount": 6},
            {"id": "subcat_edu_3", "name": {"en": "Scholarships", "si": "ශිෂ්‍යත්ව", "ta": "ஆண்டவனம்"}, "description": "Apply for scholarships and financial aid", "keywords": ["scholarship", "grant", "aid"], "itemCount": 15},
            {"id": "subcat_edu_4", "name": {"en": "Certificates", "si": "අධ්‍යාපන සහතික", "ta": "கல්வி சொன்றிதழ்"}, "description": "Request official certificates", "keywords": ["certificate", "transcript"], "itemCount": 7},
            {"id": "subcat_edu_5", "name": {"en": "Online Learning", "si": "ඔනිලයින් ඉගෙනුම", "ta": "ஆன்லைன் கற்றல்"}, "description": "Access online courses and resources", "keywords": ["online", "course", "learning"], "itemCount": 10},
            {"id": "subcat_edu_6", "name": {"en": "Teacher Training", "si": "ගුරු පුහුණු", "ta": "ஆசிரியர் பயிற்சி"}, "description": "Professional development for teachers", "keywords": ["teacher", "training", "professional"], "itemCount": 8},
            {"id": "subcat_edu_7", "name": {"en": "STEM Programs", "si": "STEM වැඩසටහන්", "ta": "STEM திட்டங்கள்"}, "description": "Science and technology education", "keywords": ["STEM", "science", "technology"], "itemCount": 9},
            {"id": "subcat_edu_8", "name": {"en": "Vocational Training", "si": "වෘත්තිමය", "ta": "தொழிலதாரி பயிற்சி"}, "description": "Technical and vocational programs", "keywords": ["vocational", "technical", "training"], "itemCount": 11},
            {"id": "subcat_edu_9", "name": {"en": "Student Support", "si": "ශිෂ්‍ය සහාය", "ta": "மாணவர் ஆதரவு"}, "description": "Counseling and support services", "keywords": ["support", "counseling", "student"], "itemCount": 6},
            {"id": "subcat_edu_10", "name": {"en": "Special Education", "si": "විශේෂ අධ්‍යාපනය", "ta": "சிறப்பு கல்வி"}, "description": "Programs for special needs", "keywords": ["special", "education", "needs"], "itemCount": 7},
            {"id": "subcat_edu_11", "name": {"en": "Higher Education", "si": "ඉහළ අධ්‍යාපනය", "ta": "உயர் கல්வி"}, "description": "University and postgraduate programs", "keywords": ["university", "higher", "postgraduate"], "itemCount": 12},
            {"id": "subcat_edu_12", "name": {"en": "Education Loans", "si": "අධ්‍යාපන ණය", "ta": "கல்வி கடன்"}, "description": "Education financing and loans", "keywords": ["loan", "financing", "education"], "itemCount": 8},
            {"id": "subcat_edu_13", "name": {"en": "Study Materials", "si": "අධ්‍යාපන ද්‍රව්‍ය", "ta": "கல்வி பொருள்"}, "description": "Textbooks and reference materials", "keywords": ["materials", "textbooks", "guides"], "itemCount": 9},
            {"id": "subcat_edu_14", "name": {"en": "International Programs", "si": "ගිණුම් ක්‍රම", "ta": "சர්வதேश திட්டங்கள්"}, "description": "Exchange and international education", "keywords": ["international", "exchange", "program"], "itemCount": 7},
            {"id": "subcat_edu_15", "name": {"en": "Language Programs", "si": "භාෂා වැඩසටහන්", "ta": "மொழி திட்டங்கள්"}, "description": "Foreign language learning programs", "keywords": ["language", "learning", "courses"], "itemCount": 10},
            {"id": "subcat_edu_16", "name": {"en": "Research Grants", "si": "පර්යේෂණ ඉවත්කරන්", "ta": "ஆராய்ச்சி ஭த்தா"}, "description": "Funding for academic research", "keywords": ["research", "grant", "project"], "itemCount": 6}
        ]
    },
    {
        "id": "cat_transport",
        "name": {"en": "Transport & Vehicles", "si": "ප්‍රවාහනය", "ta": "போக්குவரத்து"},
        "description": "Vehicle registration, licenses, and public transport",
        "icon": "🚗",
        "color": "#FF9800",
        "subcategories": [
            {"id": "subcat_trans_1", "name": {"en": "Vehicle Registration", "si": "වාහන ලියාපදිංචිය", "ta": "வாகன பதிவு"}, "description": "Register new vehicles", "keywords": ["vehicle", "registration"], "itemCount": 7},
            {"id": "subcat_trans_2", "name": {"en": "Driving Licenses", "si": "운전면허", "ta": "ஓட்டுநர் உரிமம்"}, "description": "Apply for driving licenses", "keywords": ["license", "driving"], "itemCount": 10},
            {"id": "subcat_trans_3", "name": {"en": "Permits", "si": "ඉඩවීම්", "ta": "அனுமதிப் பத्திரங்कल्"}, "description": "Special permits for vehicles", "keywords": ["permit", "authorization"], "itemCount": 6},
            {"id": "subcat_trans_4", "name": {"en": "Public Transport", "si": "ජනතා ප්‍රවාහන", "ta": "பொது போக்குவரத்து"}, "description": "Bus, train, and transport info", "keywords": ["bus", "train", "schedule"], "itemCount": 12},
            {"id": "subcat_trans_5", "name": {"en": "Vehicle Insurance", "si": "වාහන රක්ෂණ", "ta": "வாகன காப்பீடு"}, "description": "Insurance policies for vehicles", "keywords": ["insurance", "policy"], "itemCount": 8},
            {"id": "subcat_trans_6", "name": {"en": "Road Safety", "si": "පාර ආරක්ෂණ", "ta": "சாலை பாதுகாப்பு"}, "description": "Road safety programs and tips", "keywords": ["safety", "road", "accident"], "itemCount": 7},
            {"id": "subcat_trans_7", "name": {"en": "Vehicle Inspection", "si": "වාහන පරීක්ෂණ", "ta": "வாகன ஆய்வு"}, "description": "Vehicle fitness certificates", "keywords": ["inspection", "fitness", "certificate"], "itemCount": 9},
            {"id": "subcat_trans_8", "name": {"en": "Taxi Services", "si": "ටැක්සි සේවා", "ta": "டாக்சி சேவைகள்"}, "description": "Taxi licensing and regulations", "keywords": ["taxi", "cab", "service"], "itemCount": 6},
            {"id": "subcat_trans_9", "name": {"en": "Commercial Vehicles", "si": "වාණිජ වාහන", "ta": "வணிக வாகன"}, "description": "Commercial transport licensing", "keywords": ["commercial", "truck", "transport"], "itemCount": 8},
            {"id": "subcat_trans_10", "name": {"en": "Traffic Violations", "si": "ගමනාගමන උල්ලංඝන", "ta": "போக்குவரத்து மீறல्"}, "description": "Report and check violations", "keywords": ["violation", "fine", "traffic"], "itemCount": 7},
            {"id": "subcat_trans_11", "name": {"en": "Number Plates", "si": "අංකසටහන්", "ta": "பதிவு தட్టu"}, "description": "Vehicle number plate allocation", "keywords": ["number plate", "registration"], "itemCount": 6},
            {"id": "subcat_trans_12", "name": {"en": "Transit Pass", "si": "ගමනාගමන පත්‍ර", "ta": "போக्குवरत्तु अनुमति"}, "description": "Inter-city transit passes", "keywords": ["transit", "pass", "ticket"], "itemCount": 5},
            {"id": "subcat_trans_13", "name": {"en": "Vehicle Modification", "si": "වාහන සංවර්ධනය", "ta": "वाकन मारम"}, "description": "Vehicle modification approval", "keywords": ["modification", "upgrade", "change"], "itemCount": 6},
            {"id": "subcat_trans_14", "name": {"en": "Parking Services", "si": "අවතැන් සේවා", "ta": "वाकन निरुत्तम"}, "description": "Parking permits and facilities", "keywords": ["parking", "permit", "facility"], "itemCount": 7},
            {"id": "subcat_trans_15", "name": {"en": "Fuel Efficiency", "si": "ඉන්ධන", "ta": "एरिபोरुट्टु विभाग"}, "description": "Eco-friendly driving programs", "keywords": ["fuel", "efficiency", "eco-friendly"], "itemCount": 5},
            {"id": "subcat_trans_16", "name": {"en": "Vehicle Disposal", "si": "වාහන බැහැර", "ta": "वाकन अकर्षम"}, "description": "Vehicle deregistration and disposal", "keywords": ["disposal", "deregistration", "scrap"], "itemCount": 4}
        ]
    },
    {
        "id": "cat_land",
        "name": {"en": "Land & Housing", "si": "භූමි/නිවාස", "ta": "నిలम् మర్సుమ్"},
        "description": "Land registration, housing schemes, and property",
        "icon": "🏠",
        "color": "#8E7CC3",
        "subcategories": [
            {"id": "subcat_land_1", "name": {"en": "Land Registration", "si": "ඉඩම් ලියාපදිංචිය", "ta": "నిలప్ పదివు"}, "description": "Register land and property", "keywords": ["land", "registration"], "itemCount": 8},
            {"id": "subcat_land_2", "name": {"en": "Housing Schemes", "si": "නිවාස යෝජනා", "ta": "వీడు టిడపల్"}, "description": "Government housing programs", "keywords": ["housing", "scheme"], "itemCount": 9},
            {"id": "subcat_land_3", "name": {"en": "Property Documents", "si": "දේපල දකසාර", "ta": "సపత్తు ఆవణంగల్"}, "description": "Certified property documents", "keywords": ["property", "documents"], "itemCount": 5},
            {"id": "subcat_land_4", "name": {"en": "Land Survey", "si": "ඉඩම් මිනුම්", "ta": "నిలక్ కణిప్పు"}, "description": "Land measurement and surveying", "keywords": ["survey", "measurement", "boundary"], "itemCount": 7},
            {"id": "subcat_land_5", "name": {"en": "Property Tax", "si": "දේපල බදු", "ta": "సపత్తు వరి"}, "description": "Property tax assessment", "keywords": ["tax", "assessment", "payment"], "itemCount": 10},
            {"id": "subcat_land_6", "name": {"en": "Building Permission", "si": "ගොඩනැගිම්", "ta": "కట్డటం అనుమతి"}, "description": "Construction and building permits", "keywords": ["building", "permission", "construction"], "itemCount": 8},
            {"id": "subcat_land_7", "name": {"en": "Mortgage Services", "si": "උසස ණය", "ta": "కుడిసై వసతి"}, "description": "Property mortgages and loans", "keywords": ["mortgage", "loan", "property"], "itemCount": 9},
            {"id": "subcat_land_8", "name": {"en": "Tenancy Registration", "si": "කුලිය ලියාපදිංචිය", "ta": "కుత్తకే పదివు"}, "description": "Rental agreement registration", "keywords": ["tenancy", "rental", "agreement"], "itemCount": 6},
            {"id": "subcat_land_9", "name": {"en": "Boundary Disputes", "si": "සීමා බිම්", "ta": "ఎల్లై చండి"}, "description": "Resolution of boundary disputes", "keywords": ["boundary", "dispute", "resolution"], "itemCount": 5},
            {"id": "subcat_land_10", "name": {"en": "Land Lease", "si": "ඉඩම් පතනය", "ta": "నిలక్ కుత్తకే"}, "description": "Long-term land lease agreements", "keywords": ["lease", "land", "agreement"], "itemCount": 7},
            {"id": "subcat_land_11", "name": {"en": "Property Transfer", "si": "දේපල හුවමාරු", "ta": "సపత్తు మారం"}, "description": "Property ownership transfer", "keywords": ["transfer", "ownership", "change"], "itemCount": 8},
            {"id": "subcat_land_12", "name": {"en": "Environmental Clearance", "si": "පරිසර", "ta": "సూళ్ ఆమోదనై"}, "description": "Environmental permits for projects", "keywords": ["environmental", "clearance", "permit"], "itemCount": 6},
            {"id": "subcat_land_13", "name": {"en": "Economic Zones", "si": "විශේෂ ආර්ථික", "ta": "సిరప్పు పోరుట్టం"}, "description": "Land for industrial and business", "keywords": ["SEZ", "industrial", "business"], "itemCount": 5},
            {"id": "subcat_land_14", "name": {"en": "Urban Planning", "si": "නාගරික", "ta": "నగర టిడపలనం"}, "description": "City development and planning", "keywords": ["urban", "planning", "development"], "itemCount": 7},
            {"id": "subcat_land_15", "name": {"en": "Land Disputes", "si": "ඉඩම් ගැටලු", "ta": "నిలక్ కోర్టు"}, "description": "Land court and dispute resolution", "keywords": ["dispute", "settlement", "court"], "itemCount": 6},
            {"id": "subcat_land_16", "name": {"en": "Land Valuation", "si": "ඉඩම් තක්සේරුව", "ta": "నిలత్తిన్ మతిప్పు"}, "description": "Property valuation services", "keywords": ["valuation", "appraisal", "value"], "itemCount": 5}
        ]
    },
    {
        "id": "cat_elections",
        "name": {"en": "Elections & Voting", "si": "ඡන්දය", "ta": "తేర్తల్ మరుమ్"},
        "description": "Voter registration, polling information",
        "icon": "🗳️",
        "color": "#2196F3",
        "subcategories": [
            {"id": "subcat_elec_1", "name": {"en": "Voter Registration", "si": "ඡන්ද ලියාපදිංචිය", "ta": "వాక్కాలర్ పదివు"}, "description": "Register to vote", "keywords": ["voter", "registration"], "itemCount": 6},
            {"id": "subcat_elec_2", "name": {"en": "Polling Information", "si": "ඡන්ද රැස්වීම්", "ta": "వాక్కుచ్ సేతనత్తిన్"}, "description": "Find polling stations", "keywords": ["polling", "station"], "itemCount": 4},
            {"id": "subcat_elec_3", "name": {"en": "Candidate Info", "si": "ඡන්ද ලිපිකරුවරුන්", "ta": "విణప్పల్ నపర్"}, "description": "View candidate profiles", "keywords": ["candidate", "profile"], "itemCount": 3},
            {"id": "subcat_elec_4", "name": {"en": "Election Schedule", "si": "ඡන්ද දින", "ta": "తేర్తల్ అత్తవణై"}, "description": "Election dates and schedules", "keywords": ["election", "date", "schedule"], "itemCount": 5},
            {"id": "subcat_elec_5", "name": {"en": "Voter ID", "si": "ඡන්ද සනාක්ෂණ", "ta": "వాక్కాలర్ అడయానం"}, "description": "Voter ID card applications", "keywords": ["ID", "card", "voter"], "itemCount": 7},
            {"id": "subcat_elec_6", "name": {"en": "Postal Voting", "si": "තැපැල් ඡන්දය", "ta": "తపాల్ వాక్కు"}, "description": "Postal and remote voting", "keywords": ["postal", "voting", "remote"], "itemCount": 6},
            {"id": "subcat_elec_7", "name": {"en": "Campaign Info", "si": "ඡන්ද ව්‍යාපාරයේ", "ta": "తేర్తల్ ప్రచారం"}, "description": "Electoral campaign regulations", "keywords": ["campaign", "regulation", "electoral"], "itemCount": 5},
            {"id": "subcat_elec_8", "name": {"en": "Vote Counting", "si": "ඡන්ද ගිණුම්", "ta": "వాక్కు ఎణుతల్"}, "description": "Vote counting and verification", "keywords": ["counting", "verification", "result"], "itemCount": 4},
            {"id": "subcat_elec_9", "name": {"en": "Election Observers", "si": "ඡන්ද සිතිකරුවරු", "ta": "తేర్తల్ పర్యవేక్షణక్కారర్"}, "description": "Observer registration", "keywords": ["observer", "monitoring", "election"], "itemCount": 5},
            {"id": "subcat_elec_10", "name": {"en": "Electoral Disputes", "si": "ඡන්ද ගැටලුවන්", "ta": "తేర్తల్ చండి"}, "description": "Dispute resolution", "keywords": ["dispute", "complaint", "resolution"], "itemCount": 6},
            {"id": "subcat_elec_11", "name": {"en": "Party Registration", "si": "පක්ෂ ලියාපදිංචිය", "ta": "కత్సి పదివు"}, "description": "Political party registration", "keywords": ["party", "registration", "political"], "itemCount": 4},
            {"id": "subcat_elec_12", "name": {"en": "Voting Machines", "si": "ඡන්ද යන්ත්‍ර", "ta": "వాక్కు ఇయన్త్రంగల్"}, "description": "EVM and voting technology", "keywords": ["machine", "EVM", "technology"], "itemCount": 5},
            {"id": "subcat_elec_13", "name": {"en": "Voter Education", "si": "ඡන්දක අධ්‍යාපනය", "ta": "వాక్కాలర్ కల్వి"}, "description": "Civic education and awareness", "keywords": ["education", "awareness", "civic"], "itemCount": 7},
            {"id": "subcat_elec_14", "name": {"en": "Delimitation", "si": "ඡන්ද කලාපයන්", "ta": "వాక్కు విభాగంగల్"}, "description": "Electoral constituency info", "keywords": ["constituency", "delimitation", "boundary"], "itemCount": 4},
            {"id": "subcat_elec_15", "name": {"en": "Minority Rights", "si": "සුවිශේෂ අයිති", "ta": "సిరుపాన్మై ఉరిమైకల్"}, "description": "Minority voting rights", "keywords": ["minority", "rights", "protection"], "itemCount": 3},
            {"id": "subcat_elec_16", "name": {"en": "International Voting", "si": "ජාතර්ජාතික", "ta": "సర్వదేశ తేర్తల్"}, "description": "Elections abroad and diaspora", "keywords": ["international", "abroad", "diaspora"], "itemCount": 4}
        ]
    }
]

categories_col.insert_many(enhanced_categories)
print(f"✓ Inserted {len(enhanced_categories)} categories with subcategories")

enhanced_officers = [
    {"id": "off_it_01", "name": "Ms. Nayana Perera", "role": "Director - Digital Services", "department": "Ministry of IT", "email": "nayana.perera@it.gov.lk", "phone": "+94-71-123-4567", "specialization": "Digital Transformation", "bio": "Leads digital transformation initiatives"},
    {"id": "off_it_02", "name": "Mr. Ajith Wijesinghe", "role": "Chief Technology Officer", "department": "Ministry of IT", "email": "ajith.w@it.gov.lk", "phone": "+94-71-234-5678", "specialization": "Cybersecurity", "bio": "Oversees IT infrastructure and security"},
    {"id": "off_health_01", "name": "Dr. Suresh Kumar", "role": "Chief Medical Officer", "department": "Ministry of Health", "email": "suresh.kumar@health.gov.lk", "phone": "+94-11-123-4567", "specialization": "Public Health", "bio": "Leads healthcare policy"},
    {"id": "off_health_02", "name": "Dr. Kamala Wijesundara", "role": "Director of Wellness", "department": "Ministry of Health", "email": "kamala.w@health.gov.lk", "phone": "+94-11-234-5678", "specialization": "Health Promotion", "bio": "Manages wellness initiatives"},
    {"id": "off_edu_01", "name": "Mr. Rohan Silva", "role": "Assistant Secretary - Education", "department": "Ministry of Education", "email": "rohan.silva@edu.gov.lk", "phone": "+94-71-111-2222", "specialization": "Educational Planning", "bio": "Manages school programs"},
    {"id": "off_edu_02", "name": "Ms. Priya Mendis", "role": "Manager - Scholarships", "department": "Ministry of Education", "email": "priya.m@edu.gov.lk", "phone": "+94-71-222-3333", "specialization": "Student Support", "bio": "Administers scholarship programs"},
    {"id": "off_transport_01", "name": "Mr. Lasantha Perera", "role": "Director - Vehicle Registration", "department": "Ministry of Transport", "email": "lasantha.p@transport.gov.lk", "phone": "+94-71-333-4444", "specialization": "Vehicle Management", "bio": "Oversees vehicle registration"}
]

officers_col.insert_many(enhanced_officers)
print(f"✓ Inserted {len(enhanced_officers)} officer profiles")

enhanced_ads = [
    {"id": "ad_digital_training", "title": "Free Digital Skills Training Program", "body": "Enroll now for government-sponsored digital skills training.", "type": "training", "targetAudience": ["youth"], "link": "https://training.gov.lk/digital-skills", "startDate": "2026-02-15", "endDate": "2026-03-15", "priority": "high"},
    {"id": "ad_exam_results", "title": "Online Exam Results Portal Now Live", "body": "Check your latest exam results instantly", "type": "announcement", "targetAudience": ["students"], "link": "https://results.gov.lk/portal", "startDate": "2026-01-01", "priority": "medium"},
    {"id": "ad_water_scheme", "title": "New Water Connection - Zero Fee", "body": "Apply for new water connection this month", "type": "promotion", "targetAudience": ["residents"], "link": "https://water.gov.lk/apply", "startDate": "2026-02-01", "endDate": "2026-02-28", "priority": "high"},
    {"id": "ad_health_camp", "title": "Free Health Screening Camp", "body": "Get your health checked by certified professionals", "type": "event", "targetAudience": ["general-public"], "link": "https://health.gov.lk/camps", "startDate": "2026-02-20", "endDate": "2026-03-20", "priority": "medium"},
    {"id": "ad_voting_reminder", "title": "Check Your Voter Registration", "body": "Ensure you are registered to vote", "type": "important", "targetAudience": ["voters"], "link": "https://elections.gov.lk/check", "priority": "urgent"},
    {"id": "ad_driving_license", "title": "Online Driving License Application", "body": "Apply for your driving license online", "type": "announcement", "targetAudience": ["youth"], "link": "https://transport.gov.lk/apply-license", "priority": "medium"},
    {"id": "ad_housing_scheme", "title": "Affordable Housing Scheme 2026", "body": "Apply for government housing with low-interest loans", "type": "promotion", "targetAudience": ["families"], "link": "https://housing.gov.lk/2026", "startDate": "2026-02-01", "endDate": "2026-04-30", "priority": "high"}
]

ads_col.insert_many(enhanced_ads)
print(f"✓ Inserted {len(enhanced_ads)} advertisements")

print("\n✅ Enhanced seed data loaded successfully!")
print(f"   - {len(enhanced_categories)} categories")
print(f"   - {sum(len(c['subcategories']) for c in enhanced_categories)} subcategories (16 each)")
print(f"   - {len(enhanced_officers)} officers")
print(f"   - {len(enhanced_ads)} advertisements")
