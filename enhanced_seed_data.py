"""
Enhanced Seed Data with Subcategories and Rich Content Structure
This file provides a more comprehensive data structure with nested categories and detailed information.
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

# Enhanced categories with 15+ subcategories for each
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
            {"id": "subcat_it_4", "name": {"en": "Web Development Services", "si": "වෙබ් සේවා", "ta": "வலை சேவைகள்"}, "description": "Government website development", "keywords": ["web", "development", "website"], "itemCount": 6},
            {"id": "subcat_it_5", "name": {"en": "Mobile App Development", "si": "මෝබයිල් යෙදුම්", "ta": "மொபைல் பயன்பாடு"}, "description": "Government mobile applications", "keywords": ["mobile", "app", "development"], "itemCount": 7},
            {"id": "subcat_it_6", "name": {"en": "Cybersecurity Services", "si": "සයිබර් ආරක්ෂණ", "ta": "சைபர் பாதுகாப்பு"}, "description": "Data protection and security solutions", "keywords": ["security", "cyber", "protection"], "itemCount": 9},
            {"id": "subcat_it_7", "name": {"en": "Cloud Computing", "si": "මේघ පරිගණන", "ta": "கிளவுட் கணினி"}, "description": "Cloud infrastructure and services", "keywords": ["cloud", "computing", "infrastructure"], "itemCount": 8},
            {"id": "subcat_it_8", "name": {"en": "Data Analytics", "si": "දත්ත විශ්ලේෂණ", "ta": "தரவு பகுப்பாய்வு"}, "description": "Business intelligence and analytics", "keywords": ["data", "analytics", "intelligence"], "itemCount": 6},
            {"id": "subcat_it_9", "name": {"en": "AI & Machine Learning", "si": "කෘත්‍රිම බුද්ධිමත්තාව", "ta": "செயற்கை நுண்ணறிவு"}, "description": "Artificial intelligence solutions", "keywords": ["AI", "machine learning", "automation"], "itemCount": 5},
            {"id": "subcat_it_10", "name": {"en": "Blockchain Services", "si": "බ්ලොකචේන්", "ta": "பிளாக்செயின்"}, "description": "Blockchain and distributed ledger technology", "keywords": ["blockchain", "ledger", "cryptocurrency"], "itemCount": 4},
            {"id": "subcat_it_11", "name": {"en": "IT Consultancy", "si": "IT උපදෙස්", "ta": "ஐடி ஆலோசனை"}, "description": "Technology consulting and advisory", "keywords": ["consultancy", "advisory", "consulting"], "itemCount": 7},
            {"id": "subcat_it_12", "name": {"en": "System Administration", "si": "පද්ධති පරිපාලනය", "ta": "கணினி நிர்வாகம்"}, "description": "Server and network management", "keywords": ["system", "administration", "network"], "itemCount": 8},
            {"id": "subcat_it_13", "name": {"en": "Database Management", "si": "දත්ත සමුදාය", "ta": "தரவுத்தளம்"}, "description": "Database design and maintenance", "keywords": ["database", "SQL", "management"], "itemCount": 6},
            {"id": "subcat_it_14", "name": {"en": "IT Infrastructure", "si": "IT ඉතිරුව", "ta": "ஐடி உள்கட்டமைப்பு"}, "description": "Complete IT infrastructure setup", "keywords": ["infrastructure", "hardware", "setup"], "itemCount": 9},
            {"id": "subcat_it_15", "name": {"en": "Software Testing", "si": "මෘදුවේරේ පරීක්ෂණ", "ta": "மென்பொருள் சோதனை"}, "description": "QA and software quality assurance", "keywords": ["testing", "QA", "quality"], "itemCount": 7},
            {"id": "subcat_it_16", "name": {"en": "IT Project Management", "si": "IT ව්‍යාපෘති", "ta": "ஐடி திட்ட மேலாண்மை"}, "description": "Project planning and execution", "keywords": ["project", "management", "planning"], "itemCount": 8}
        ]
    },
    {
        "id": "cat_health",
        "name": {"en": "Health & Medical Services", "si": "සෞඛ්‍ය සේවා", "ta": "சுகாதார சேவைகள்"},
        "description": "Healthcare, medical certificates, and wellness programs",
        "icon": "🏥",
        "color": "#D32F2F",
        "subcategories": [
            {"id": "subcat_health_1", "name": {"en": "Medical Certificates", "si": "වෛද්‍ය සහතික", "ta": "மருத்துவ சொன்றிதழ்"}, "description": "Apply for medical certificates", "keywords": ["medical", "certificate"], "itemCount": 7},
            {"id": "subcat_health_2", "name": {"en": "Vaccination Programs", "si": "ශරීර ගතිකතා", "ta": "தடுப்பூசி"}, "description": "Immunization schedules", "keywords": ["vaccination", "vaccine"], "itemCount": 6},
            {"id": "subcat_health_3", "name": {"en": "Health Insurance", "si": "සෞඛ්‍ය රක්ෂණ", "ta": "சுகாதார காப்பீடு"}, "description": "Government insurance schemes", "keywords": ["insurance", "coverage"], "itemCount": 9},
            {"id": "subcat_health_4", "name": {"en": "Wellness Programs", "si": "සුබ දල", "ta": "ஆரோக்கிய திட்டங்கள்"}, "description": "Health promotion initiatives", "keywords": ["wellness", "prevention"], "itemCount": 5},
            {"id": "subcat_health_5", "name": {"en": "Disease Prevention", "si": "රෝග නිරෝධන", "ta": "நோய் தடுப்பு"}, "description": "Disease control programs", "keywords": ["disease", "prevention", "control"], "itemCount": 8},
            {"id": "subcat_health_6", "name": {"en": "Hospital Services", "si": "රෝහල් සේවා", "ta": "மருத்துவமனை சேவைகள்"}, "description": "Hospital admission and procedures", "keywords": ["hospital", "admission", "service"], "itemCount": 10},
            {"id": "subcat_health_7", "name": {"en": "Emergency Care", "si": "හදිසි ප්‍රතිකාර", "ta": "அவசர சிகிச்சை"}, "description": "Emergency medical services", "keywords": ["emergency", "urgent", "care"], "itemCount": 6},
            {"id": "subcat_health_8", "name": {"en": "Maternal Care", "si": "මවුවතා සිටුවාවු", "ta": "தாய் சிகிச்சை"}, "description": "Pregnancy and childbirth services", "keywords": ["maternal", "pregnancy", "childbirth"], "itemCount": 7},
            {"id": "subcat_health_9", "name": {"en": "Child Health", "si": "ළමා සෞඛ්‍ය", "ta": "குழந்தை சுகாதாரம்"}, "description": "Pediatric and child health services", "keywords": ["child", "pediatric", "health"], "itemCount": 8},
            {"id": "subcat_health_10", "name": {"en": "Mental Health", "si": "මානසික සෞඛ්‍ය", "ta": "மனநல சேவை"}, "description": "Mental health and counseling", "keywords": ["mental", "psychology", "counseling"], "itemCount": 6},
            {"id": "subcat_health_11", "name": {"en": "Dental Care", "si": "දතු සිතුවාවු", "ta": "பல் சிகிச்சை"}, "description": "Dental health and treatment", "keywords": ["dental", "teeth", "care"], "itemCount": 5},
            {"id": "subcat_health_12", "name": {"en": "Eye Care", "si": "ඇසින් සිතුවාවු", "ta": "கண் சிகிச்சை"}, "description": "Ophthalmology services", "keywords": ["eye", "vision", "ophthalmology"], "itemCount": 5},
            {"id": "subcat_health_13", "name": {"en": "Pharmacy Services", "si": "ඖෂධ සපයාම", "ta": "மருந்து சேவைகள்"}, "description": "Prescription and medication services", "keywords": ["pharmacy", "medicine", "prescription"], "itemCount": 7},
            {"id": "subcat_health_14", "name": {"en": "Laboratory Tests", "si": "විද්‍යාගාර පරීක්ෂණ", "ta": "ஆய்வக சோதனைகள்"}, "description": "Medical laboratory services", "keywords": ["laboratory", "test", "diagnosis"], "itemCount": 9},
            {"id": "subcat_health_15", "name": {"en": "Physical Therapy", "si": "ශාරීරික ප්‍රතිකාර", "ta": "உடல் சிகிச்சை"}, "description": "Rehabilitation and therapy", "keywords": ["therapy", "rehabilitation", "physical"], "itemCount": 6},
            {"id": "subcat_health_16", "name": {"en": "Nutrition Services", "si": "පෝෂණ සेवা", "ta": "ஊட்டச்சத்து சேவைகள்"}, "description": "Nutritional counseling", "keywords": ["nutrition", "diet", "food"], "itemCount": 5}
        ]
    },
    {
        "id": "cat_education",
        "name": {"en": "Education & Training", "si": "අධ්‍යාපනය", "ta": "கல்வி"},
        "description": "School enrollment, exams, scholarships and educational support",
        "icon": "📚",
        "color": "#4CAF50",
        "subcategories": [
            {
                "id": "subcat_school_enroll",
                "name": {"en": "School Enrollment", "si": "පාසල් ඇතුළත් කිරීම", "ta": "பள்ளி சேர்க்கை"},
                "description": "Enroll in government schools and institutions",
                "keywords": ["enrollment", "admission", "school", "registration"],
                "itemCount": 8
            },
            {
                "id": "subcat_exam_results",
                "name": {"en": "Exam Results & Schedules", "si": "විභාග සිටුවම්", "ta": "பரீட்சை அட்டவணை"},
                "description": "Check exam results and view exam schedules",
                "keywords": ["exam", "results", "schedule", "test"],
                "itemCount": 4
            },
            {
                "id": "subcat_scholarships",
                "name": {"en": "Scholarships & Grants", "si": "ශිෂ්‍යත්ව", "ta": "ஆண்டவனங்கள் மற்றும் மானியம்"},
                "description": "Apply for scholarships and educational grants",
                "keywords": ["scholarship", "grant", "financial", "aid"],
                "itemCount": 15
            },
            {
                "id": "subcat_certificates",
                "name": {"en": "Education Certificates", "si": "අධ්‍යාපන සහතික", "ta": "கல்வி சொன்றிதழ்"},
                "description": "Request official educational certificates",
                "keywords": ["certificate", "transcript", "verification", "official"],
                "itemCount": 6
            }
        ]
    },
    {
        "id": "cat_transport",
        "name": {"en": "Transport & Vehicles", "si": "ප්‍රවාහනය", "ta": "போக்குவரத்து"},
        "description": "Vehicle registration, licenses, and public transport information",
        "icon": "🚗",
        "color": "#FF9800",
        "subcategories": [
            {
                "id": "subcat_vehicle_reg",
                "name": {"en": "Vehicle Registration", "si": "වාහන ලියාපදිංචිය", "ta": "வாகன பதிவு"},
                "description": "Register new vehicles and renew registrations",
                "keywords": ["vehicle", "registration", "car", "motorcycle"],
                "itemCount": 7
            },
            {
                "id": "subcat_driving_license",
                "name": {"en": "Driving Licenses", "si": "운전면허", "ta": "ஓட்டுநர் உரிமம்"},
                "description": "Apply for or renew driving licenses",
                "keywords": ["license", "driving", "test", "renewal"],
                "itemCount": 10
            },
            {
                "id": "subcat_permits",
                "name": {"en": "Permits & Authorizations", "si": "ඉඩවීම්", "ta": "அனுமதிப் பত்திரங்கள்"},
                "description": "Get special permits and authorizations",
                "keywords": ["permit", "authorization", "special", "transport"],
                "itemCount": 6
            },
            {
                "id": "subcat_public_transport",
                "name": {"en": "Public Transport Info", "si": "ජනතා ප්‍රවාහන", "ta": "பொது போக்குவரத்து"},
                "description": "Public bus, train, and transport schedules",
                "keywords": ["bus", "train", "schedule", "route"],
                "itemCount": 12
            }
        ]
    },
    {
        "id": "cat_land",
        "name": {"en": "Land & Housing", "si": "භූමි/නිවාස", "ta": "நிலம் மற்றும் வீடுகள்"},
        "description": "Land registration, housing schemes, and property documents",
        "icon": "🏠",
        "color": "#8E7CC3",
        "subcategories": [
            {
                "id": "subcat_land_registration",
                "name": {"en": "Land Registration", "si": "ඉඩම් ලියාපදිංචිය", "ta": "நிலப் பதிவு"},
                "description": "Register land and view property details",
                "keywords": ["land", "registration", "property", "title"],
                "itemCount": 8
            },
            {
                "id": "subcat_housing_scheme",
                "name": {"en": "Housing Schemes", "si": "නිවාස යෝජනා", "ta": "வீட்டு திட்டங்கள்"},
                "description": "Government housing programs and affordable housing",
                "keywords": ["housing", "scheme", "affordable", "project"],
                "itemCount": 9
            },
            {
                "id": "subcat_property_docs",
                "name": {"en": "Property Documents", "si": "දේපල ឯកសារ", "ta": "சொத்து ஆவணங்கள்"},
                "description": "Get certified property documents and certificates",
                "keywords": ["property", "documents", "certificate", "deed"],
                "itemCount": 5
            }
        ]
    },
    {
        "id": "cat_elections",
        "name": {"en": "Elections & Voting", "si": "ඡන්දය", "ta": "தேர்தல் மற்றும் வாக்கு"},
        "description": "Voter registration, polling information, and electoral procedures",
        "icon": "🗳️",
        "color": "#2196F3",
        "subcategories": [
            {
                "id": "subcat_voter_reg",
                "name": {"en": "Voter Registration", "si": "ඡන්ද ලියාපදිංචිය", "ta": "வாக்காளர் பதிவு"},
                "description": "Register to vote and check voter status",
                "keywords": ["voter", "registration", "enrollment", "election"],
                "itemCount": 6
            },
            {
                "id": "subcat_polling_info",
                "name": {"en": "Polling Information", "si": "ඡන්ද රැස්වීම් තොරතුරු", "ta": "வாக்குச் சేதனத்தின் தகவல்"},
                "description": "Find polling stations and election schedules",
                "keywords": ["polling", "station", "schedule", "election"],
                "itemCount": 4
            },
            {
                "id": "subcat_candidate_info",
                "name": {"en": "Candidate Information", "si": "ඡන්ද ලිපිකරුවරුන්ගේ තොරතුරු", "ta": "விண்ணப்ப நபர் தகவல்"},
                "description": "View candidate profiles and party information",
                "keywords": ["candidate", "party", "profile", "election"],
                "itemCount": 3
            }
        ]
    }
]

categories_col.insert_many(enhanced_categories)
print(f"✓ Inserted {len(enhanced_categories)} categories with subcategories")

# Enhanced officers with more details
enhanced_officers = [
    {
        "id": "off_it_01",
        "name": "Ms. Nayana Perera",
        "role": "Director - Digital Services",
        "department": "Ministry of IT & Digital Affairs",
        "email": "nayana.perera@it.gov.lk",
        "phone": "+94-71-123-4567",
        "specialization": "Digital Transformation, Cloud Computing",
        "bio": "Leads digital transformation initiatives with 15+ years of IT experience"
    },
    {
        "id": "off_it_02",
        "name": "Mr. Ajith Wijesinghe",
        "role": "Chief Technology Officer",
        "department": "Ministry of IT & Digital Affairs",
        "email": "ajith.w@it.gov.lk",
        "phone": "+94-71-234-5678",
        "specialization": "Cybersecurity, Infrastructure",
        "bio": "Oversees government IT infrastructure and security"
    },
    {
        "id": "off_health_01",
        "name": "Dr. Suresh Kumar",
        "role": "Chief Medical Officer",
        "department": "Ministry of Health",
        "email": "suresh.kumar@health.gov.lk",
        "phone": "+94-11-123-4567",
        "specialization": "Public Health, Epidemiology",
        "bio": "Leads healthcare policy and disease prevention programs"
    },
    {
        "id": "off_health_02",
        "name": "Dr. Kamala Wijesundara",
        "role": "Director of Wellness Programs",
        "department": "Ministry of Health",
        "email": "kamala.w@health.gov.lk",
        "phone": "+94-11-234-5678",
        "specialization": "Health Promotion, Community Health",
        "bio": "Manages national health promotion and wellness initiatives"
    },
    {
        "id": "off_edu_01",
        "name": "Mr. Rohan Silva",
        "role": "Assistant Secretary - Education",
        "department": "Ministry of Education",
        "email": "rohan.silva@edu.gov.lk",
        "phone": "+94-71-111-2222",
        "specialization": "Educational Planning, Curriculum Development",
        "bio": "Manages school programs and educational standards"
    },
    {
        "id": "off_edu_02",
        "name": "Ms. Priya Mendis",
        "role": "Manager - Scholarships",
        "department": "Ministry of Education",
        "email": "priya.m@edu.gov.lk",
        "phone": "+94-71-222-3333",
        "specialization": "Student Support, Scholarships",
        "bio": "Administers scholarship programs and student support services"
    },
    {
        "id": "off_transport_01",
        "name": "Mr. Lasantha Perera",
        "role": "Director - Vehicle Registration",
        "department": "Ministry of Transport",
        "email": "lasantha.p@transport.gov.lk",
        "phone": "+94-71-333-4444",
        "specialization": "Vehicle Management, Licensing",
        "bio": "Oversees vehicle registration and licensing systems"
    }
]

officers_col.insert_many(enhanced_officers)
print(f"✓ Inserted {len(enhanced_officers)} enhanced officer profiles")

# Enhanced ads with more details
enhanced_ads = [
    {
        "id": "ad_digital_training",
        "title": "Free Digital Skills Training Program",
        "body": "Enroll now for government-sponsored digital skills training. Learn web development, data analysis, and IT fundamentals. Limited seats available!",
        "type": "training",
        "targetAudience": ["youth", "unemployed", "students"],
        "link": "https://training.gov.lk/digital-skills",
        "startDate": "2026-02-15",
        "endDate": "2026-03-15",
        "priority": "high"
    },
    {
        "id": "ad_exam_results",
        "title": "Online Exam Results Portal Now Live",
        "body": "Check your latest exam results instantly through our secure online portal. Use your registration number and NIC to access results.",
        "type": "announcement",
        "targetAudience": ["students", "graduates"],
        "link": "https://results.gov.lk/portal",
        "startDate": "2026-01-01",
        "priority": "medium"
    },
    {
        "id": "ad_water_scheme",
        "title": "New Water Connection - Zero Processing Fee",
        "body": "Apply for new water connection this month with zero processing fees. Fast-track processing available for residential areas.",
        "type": "promotion",
        "targetAudience": ["residents", "property-owners"],
        "link": "https://water.gov.lk/apply-connection",
        "startDate": "2026-02-01",
        "endDate": "2026-02-28",
        "priority": "high"
    },
    {
        "id": "ad_health_camp",
        "title": "Free Health Screening Camp",
        "body": "Participate in our free health screening camp. Get your health checked by certified medical professionals. Available at regional centers.",
        "type": "event",
        "targetAudience": ["general-public", "seniors"],
        "link": "https://health.gov.lk/screening-camps",
        "startDate": "2026-02-20",
        "endDate": "2026-03-20",
        "priority": "medium"
    },
    {
        "id": "ad_voting_reminder",
        "title": "⚠️ Important: Check Your Voter Registration",
        "body": "Ensure you are registered to vote in the upcoming elections. Check your voter status online and update your details if needed.",
        "type": "important",
        "targetAudience": ["voters", "citizens"],
        "link": "https://elections.gov.lk/check-voter-status",
        "priority": "urgent"
    },
    {
        "id": "ad_driving_license",
        "title": "Online Driving License Application",
        "body": "Apply for your driving license online! Complete medical check and tests are now available at multiple centers.",
        "type": "announcement",
        "targetAudience": ["youth", "adults"],
        "link": "https://transport.gov.lk/apply-license",
        "priority": "medium"
    },
    {
        "id": "ad_housing_scheme",
        "title": "Affordable Housing Scheme 2026",
        "body": "Apply for government housing scheme with low-interest loans. Eligibility criteria and detailed information available on our portal.",
        "type": "promotion",
        "targetAudience": ["low-income", "families"],
        "link": "https://housing.gov.lk/2026-scheme",
        "startDate": "2026-02-01",
        "endDate": "2026-04-30",
        "priority": "high"
    }
]

ads_col.insert_many(enhanced_ads)
print(f"✓ Inserted {len(enhanced_ads)} enhanced advertisements")

print("\n✅ Enhanced seed data loaded successfully!")
print(f"   - {len(enhanced_categories)} categories with {sum(len(c['subcategories']) for c in enhanced_categories)} subcategories")
print(f"   - {len(enhanced_officers)} officers")
print(f"   - {len(enhanced_ads)} advertisements/announcements")
