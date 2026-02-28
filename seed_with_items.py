"""
Complete Seed Data with Service Items for ALL Subcategories
Each subcategory now has actual service items with details, forms, and requirements
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

# Clear existing data
categories_col.delete_many({})

# Helper function to create service items
def create_item(item_id, title_en, title_si, title_ta, description, requirements, fee, processing_time, form_fields=None):
    return {
        "id": item_id,
        "title": {
            "en": title_en,
            "si": title_si,
            "ta": title_ta
        },
        "description": description,
        "requirements": requirements,
        "fee": fee,
        "processingTime": processing_time,
        "formFields": form_fields or [],
        "downloads": [],
        "status": "active"
    }

# Complete categories with subcategories and items
complete_categories = [
    {
        "id": "cat_it",
        "name": {"en": "IT & Digital Services", "si": "තොරතුරු ශිල්පය", "ta": "தகவல் தொழில்நுட்பம்"},
        "description": "Government IT services, digital certificates, and technology support",
        "icon": "💻",
        "color": "#1976D2",
        "subcategories": [
            {
                "id": "subcat_it_1",
                "name": {"en": "Digital Certificates", "si": "ඩිජිටල් සහතික", "ta": "டிஜிட்டல் சொன்றிதழ்"},
                "description": "Apply for and manage digital certificates",
                "keywords": ["certificate", "digital", "authentication"],
                "itemCount": 5,
                "items": [
                    create_item("item_it_1_1", "SSL Certificate", "SSL සහතිකය", "SSL சொன்றிதழ்",
                               "Apply for SSL certificate for your website",
                               ["Business License", "Domain Ownership Proof", "ID Copy"],
                               "5000 LKR", "7 working days",
                               [{"name": "domain", "type": "text", "required": True}, 
                                {"name": "organization", "type": "text", "required": True}]),
                    
                    create_item("item_it_1_2", "Digital Signature", "ඩිජිටල් අත්සන", "டிஜிட்டல் கையொப்பம்",
                               "Get your official digital signature certificate",
                               ["National ID", "Passport Photo", "Email Verification"],
                               "3000 LKR", "5 working days",
                               [{"name": "fullName", "type": "text", "required": True},
                                {"name": "nic", "type": "text", "required": True}]),
                    
                    create_item("item_it_1_3", "Code Signing Certificate", "කේත අත්සන සහතිකය", "குறியீட்டு சொன்றிதழ்",
                               "Certificate for signing software and applications",
                               ["Developer License", "Company Registration", "Tax ID"],
                               "8000 LKR", "10 working days"),
                    
                    create_item("item_it_1_4", "Email Certificate", "විද්‍යුත් තැපැල් සහතිකය", "மின்னஞ்சல் சொன்றிதழ்",
                               "Secure email communication certificate",
                               ["Email Verification", "ID Proof"],
                               "2000 LKR", "3 working days"),
                    
                    create_item("item_it_1_5", "Document Signing Certificate", "ලේඛන අත්සන", "ஆவண கையொப்பம்",
                               "Certificate for digitally signing official documents",
                               ["Government Employee ID", "Department Approval"],
                               "4000 LKR", "5 working days")
                ]
            },
            {
                "id": "subcat_it_2",
                "name": {"en": "IT Training Programs", "si": "IT පුහුණු", "ta": "ஐடி பயிற்சி"},
                "description": "Free and paid training courses",
                "keywords": ["training", "course", "programming"],
                "itemCount": 8,
                "items": [
                    create_item("item_it_2_1", "Python Programming Course", "Python ක්‍රමලේඛන පාඨමාලාව", "Python நிரலாக்க பாடநெறி",
                               "Beginner to advanced Python programming",
                               ["Basic computer knowledge", "Age 16+"],
                               "Free", "12 weeks"),
                    
                    create_item("item_it_2_2", "Web Development Bootcamp", "වෙබ් සංවර්ධන පුහුණුව", "வலை மேம்பாட்டு பயிற்சி",
                               "Full-stack web development training",
                               ["Basic programming knowledge"],
                               "15000 LKR", "16 weeks"),
                    
                    create_item("item_it_2_3", "Cybersecurity Fundamentals", "සයිබර් ආරක්ෂාව", "இணைய பாதுகாப்பு",
                               "Learn basics of cybersecurity",
                               ["IT background preferred"],
                               "Free", "8 weeks"),
                    
                    create_item("item_it_2_4", "Data Science with Python", "Python සමඟ දත්ත විද්‍යාව", "Python உடன் தரவு அறிவியல்",
                               "Data analysis and machine learning",
                               ["Python knowledge", "Statistics basics"],
                               "20000 LKR", "20 weeks"),
                    
                    create_item("item_it_2_5", "Mobile App Development", "ජංගම යෙදුම් සංවර්ධනය", "மொபைல் பயன்பாடு மேம்பாடு",
                               "Android and iOS app development",
                               ["Programming experience"],
                               "18000 LKR", "14 weeks"),
                    
                    create_item("item_it_2_6", "Cloud Computing with AWS", "AWS සමඟ වලාකුළු", "AWS உடன் மேகக் கணினி",
                               "Amazon Web Services certification prep",
                               ["IT fundamentals"],
                               "25000 LKR", "10 weeks"),
                    
                    create_item("item_it_2_7", "Digital Marketing", "ඩිජිටල් අලෙවිකරණය", "டிஜிட்டல் சந்தைப்படுத்தல்",
                               "Online marketing and SEO training",
                               ["Basic computer skills"],
                               "12000 LKR", "8 weeks"),
                    
                    create_item("item_it_2_8", "Database Management", "දත්ත සමුදාය කළමනාකරණය", "தரவுத்தள மேலாண்மை",
                               "SQL and NoSQL database administration",
                               ["Basic IT knowledge"],
                               "Free", "6 weeks")
                ]
            },
            {
                "id": "subcat_it_3",
                "name": {"en": "Technical Support", "si": "තාක්ෂණ සහාය", "ta": "தொழில்நுட்ப ஆதரவு"},
                "description": "Get help with technical issues",
                "keywords": ["support", "help", "troubleshooting"],
                "itemCount": 6,
                "items": [
                    create_item("item_it_3_1", "Government Website Support", "රජයේ වෙබ් අඩවි සහාය", "அரசு இணையதள ஆதரவு",
                               "Technical support for government portals",
                               ["Issue description", "Screenshot if applicable"],
                               "Free", "24-48 hours"),
                    
                    create_item("item_it_3_2", "Email Setup Assistance", "විද්‍යුත් තැපැල් සැකසීම", "மின்னஞ்சல் அமைப்பு",
                               "Help setting up government email accounts",
                               ["Employee ID"],
                               "Free", "Same day"),
                    
                    create_item("item_it_3_3", "Software Installation Help", "මෘදුකාංග ස්ථාපනය", "மென்பொருள் நிறுவல்",
                               "Assistance with government software",
                               ["System details", "Error messages"],
                               "Free", "1-2 days"),
                    
                    create_item("item_it_3_4", "Network Troubleshooting", "ජාල දෝෂ නිරාකරණය", "வலைப்பின்னல் சரிசெய்தல்",
                               "Resolve network connectivity issues",
                               ["Network details"],
                               "Free", "4 hours"),
                    
                    create_item("item_it_3_5", "Password Reset", "මුරපදය යළි සැකසීම", "கடவுச்சொல் மீட்டமை",
                               "Reset forgotten passwords for government systems",
                               ["Employee ID", "Email verification"],
                               "Free", "Immediate"),
                    
                    create_item("item_it_3_6", "Hardware Support Request", "දෘඩාංග සහාය", "வன்பொருள் ஆதரவு",
                               "Request hardware repair or replacement",
                               ["Device details", "Issue description"],
                               "Free", "3-5 days")
                ]
            },
            # Add more IT subcategories with items...
        ]
    },
    {
        "id": "cat_health",
        "name": {"en": "Health & Medical", "si": "සෞඛ්‍ය සේවා", "ta": "சுகாதார சேவைகள்"},
        "description": "Healthcare, medical certificates, and wellness programs",
        "icon": "🏥",
        "color": "#D32F2F",
        "subcategories": [
            {
                "id": "subcat_health_1",
                "name": {"en": "Medical Certificates", "si": "වෛද්‍ය සහතික", "ta": "மருத்துவ சொன்றிதழ்"},
                "description": "Apply for medical certificates",
                "keywords": ["medical", "certificate", "health"],
                "itemCount": 7,
                "items": [
                    create_item("item_health_1_1", "Fitness Certificate", "යෝග්‍යතා සහතිකය", "உடற்தகுதி சொன்றிதழ்",
                               "Certificate of physical fitness",
                               ["Medical examination", "ID proof", "Recent photo"],
                               "500 LKR", "3 days"),
                    
                    create_item("item_health_1_2", "Sick Leave Certificate", "රෝග නිවාඩු සහතිකය", "நோய் விடுப்பு சொன்றிதழ்",
                               "Medical certificate for sick leave",
                               ["Doctor's note", "Medical report"],
                               "300 LKR", "Same day"),
                    
                    create_item("item_health_1_3", "Mental Health Certificate", "මානසික සෞඛ්‍ය සහතිකය", "மன நலச் சொன்றிதழ்",
                               "Certificate from psychiatrist",
                               ["Psychiatric evaluation", "Medical history"],
                               "1500 LKR", "7 days"),
                    
                    create_item("item_health_1_4", "Maternity Leave Certificate", "මාතෘ නිවාඩු සහතිකය", "மகப்பேறு விடுப்பு சொன்றிதழ்",
                               "Certificate for maternity leave",
                               ["Pregnancy confirmation", "Expected delivery date"],
                               "Free", "Same day"),
                    
                    create_item("item_health_1_5", "Vaccination Certificate", "එන්නත් සහතිකය", "தடுப்பூசி சொன்றிதழ்",
                               "Certificate of vaccination",
                               ["Vaccination record"],
                               "Free", "Immediate"),
                    
                    create_item("item_health_1_6", "Pre-Employment Medical", "රැකියා පෙර වෛද්‍ය පරීක්ෂණය", "வேலைக்கு முன் மருத்துவம்",
                               "Medical examination for employment",
                               ["Employer letter", "ID proof"],
                               "2000 LKR", "5 days"),
                    
                    create_item("item_health_1_7", "Disability Certificate", "ආබාධිත සහතිකය", "ஊனமுற்றோர் சொன்றிதழ்",
                               "Certificate for disability benefits",
                               ["Medical assessment", "Supporting documents"],
                               "Free", "14 days")
                ]
            },
            {
                "id": "subcat_health_2",
                "name": {"en": "Vaccination Services", "si": "එන්නත් සේවා", "ta": "தடுப்பூசி சேவைகள்"},
                "description": "Immunization schedules and vaccines",
                "keywords": ["vaccination", "vaccine", "immunization"],
                "itemCount": 6,
                "items": [
                    create_item("item_health_2_1", "COVID-19 Vaccination", "COVID-19 එන්නත", "COVID-19 தடுப்பூசி",
                               "Register for COVID-19 vaccine",
                               ["NIC", "Health condition declaration"],
                               "Free", "1-3 days"),
                    
                    create_item("item_health_2_2", "Child Immunization", "ළමා එන්නත්", "குழந்தை தடுப்பூசி",
                               "Regular immunization for children",
                               ["Birth certificate", "Parent ID"],
                               "Free", "Scheduled"),
                    
                    create_item("item_health_2_3", "Travel Vaccination", "සංචාරක එන්නත්", "பயண தடுப்பூசி",
                               "Vaccines for international travel",
                               ["Passport", "Travel itinerary"],
                               "Varies", "7-14 days"),
                    
                    create_item("item_health_2_4", "Flu Shot", "උණ එන්නත", "காய்ச்சல் தடுப்பூசி",
                               "Annual influenza vaccination",
                               ["ID proof"],
                               "500 LKR", "Same day"),
                    
                    create_item("item_health_2_5", "HPV Vaccine", "HPV එන්නත", "HPV தடுப்பூசி",
                               "Human papillomavirus vaccination",
                               ["Age 9-26", "Parental consent if minor"],
                               "Free for eligible", "Scheduled"),
                    
                    create_item("item_health_2_6", "Tetanus Vaccine", "ටෙටනස් එන්නත", "டெட்டானஸ் தடுப்பூசி",
                               "Tetanus immunization",
                               ["Medical history"],
                               "200 LKR", "Same day")
                ]
            },
            # Add more health subcategories...
        ]
    },
    {
        "id": "cat_education",
        "name": {"en": "Education & Learning", "si": "අධ්‍යාපනය", "ta": "கல்வி"},
        "description": "School enrollment, exam results, scholarships",
        "icon": "📚",
        "color": "#4CAF50",
        "subcategories": [
            {
                "id": "subcat_edu_1",
                "name": {"en": "School Enrollment", "si": "පාසල් ඇතුළත් වීම", "ta": "பள்ளி சேர்க்கை"},
                "description": "Register for school admission",
                "keywords": ["school", "enrollment", "admission"],
                "itemCount": 5,
                "items": [
                    create_item("item_edu_1_1", "Grade 1 Admission", "1 ශ්‍රේණිය ඇතුළත්", "வகுப்பு 1 சேர்க்கை",
                               "Apply for Grade 1 admission",
                               ["Birth certificate", "Proof of residence", "Parent ID"],
                               "Free", "30 days"),
                    
                    create_item("item_edu_1_2", "Transfer Certificate", "මාරු සහතිකය", "இடமாற்ற சொன்றிதழ்",
                               "School transfer certificate",
                               ["Current school leaving certificate", "Reason for transfer"],
                               "100 LKR", "7 days"),
                    
                    create_item("item_edu_1_3", "Distance Education Enrollment", "දුරස්ථ අධ්‍යාපනය", "தொலைதூரக் கல்வி",
                               "Enroll in distance learning programs",
                               ["Previous education certificates", "Age proof"],
                               "Varies", "14 days"),
                    
                    create_item("item_edu_1_4", "International School Admission", "ජාත්‍යන්තර පාසල්", "சர்வதேச பள்ளி",
                               "Application for international schools",
                               ["Academic records", "Language proficiency", "Passport"],
                               "Varies", "45 days"),
                    
                    create_item("item_edu_1_5", "Special Needs Education", "විශේෂ අධ්‍යාපනය", "சிறப்புக் கல்வி",
                               "Enrollment for special education",
                               ["Medical assessment", "Psychologist report"],
                               "Free", "21 days")
                ]
            },
            {
                "id": "subcat_edu_2",
                "name": {"en": "Scholarships", "si": "ශිෂ්‍යත්ව", "ta": "உதவித்தொகை"},
                "description": "Apply for scholarships and financial aid",
                "keywords": ["scholarship", "grant", "financial aid"],
                "itemCount": 8,
                "items": [
                    create_item("item_edu_2_1", "Merit-Based Scholarship", "කුසලතා ශිෂ්‍යත්වය", "தகுதி அடிப்படை உதவித்தொகை",
                               "Scholarship based on academic merit",
                               ["Academic transcripts", "Recommendation letters"],
                               "Free to apply", "60 days"),
                    
                    create_item("item_edu_2_2", "Need-Based Financial Aid", "අවශ්‍යතා මූල්‍ය ආධාර", "தேவை அடிப்படை உதவி",
                               "Financial assistance for low-income families",
                               ["Income certificate", "Family details"],
                               "Free", "45 days"),
                    
                    create_item("item_edu_2_3", "Sports Scholarship", "ක්‍රීඩා ශිෂ්‍යත්වය", "விளையாட்டு உதவித்தொகை",
                               "Scholarship for talented athletes",
                               ["Sports achievements", "Coach recommendation"],
                               "Free", "90 days"),
                    
                    create_item("item_edu_2_4", "STEM Scholarship", "STEM ශිෂ්‍යත්වය", "STEM உதவித்தொகை",
                               "Scholarship for science and technology students",
                               ["Academic records in science", "Project portfolio"],
                               "Free", "60 days"),
                    
                    create_item("item_edu_2_5", "Arts & Culture Scholarship", "කලා ශිෂ්‍යත්වය", "கலை உதவித்தொகை",
                               "Support for arts students",
                               ["Portfolio", "Performance records"],
                               "Free", "60 days"),
                    
                    create_item("item_edu_2_6", "Minority Scholarship", "සුළුතර ශිෂ්‍යත්වය", "சிறுபான்மை உதவித்தொகை",
                               "Scholarship for minority communities",
                               ["Community certificate", "Academic records"],
                               "Free", "45 days"),
                    
                    create_item("item_edu_2_7", "Postgraduate Research Grant", "පශ්චාත් උපාධි", "முதுகலை ஆராய்ச்சி",
                               "Research funding for postgraduate students",
                               ["Research proposal", "Supervisor recommendation"],
                               "Free", "90 days"),
                    
                    create_item("item_edu_2_8", "International Study Scholarship", "විදේශ අධ්‍යාපනය", "வெளிநாட்டு கல்வி",
                               "Scholarship for overseas education",
                               ["Admission letter", "Academic excellence", "Passport"],
                               "Free", "120 days")
                ]
            },
        ]
    }
]

# Insert complete data
print("\n🌱 Seeding categories with service items...")
result = categories_col.insert_many(complete_categories)
print(f"✅ Inserted {len(result.inserted_ids)} categories")

# Count total subcategories and items
total_subcategories = 0
total_items = 0
for cat in complete_categories:
    subs = cat.get("subcategories", [])
    total_subcategories += len(subs)
    for sub in subs:
        total_items += len(sub.get("items", []))

print(f"✅ Total subcategories: {total_subcategories}")
print(f"✅ Total service items: {total_items}")
print("\n✨ Database seeded successfully!")
print("📊 Next step: Run your app and build the AI index from admin panel")