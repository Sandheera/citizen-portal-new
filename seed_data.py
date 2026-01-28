from pymongo import MongoClient
import os, json, pathlib
from dotenv import load_dotenv

load_dotenv()  # Load .env file
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000, connectTimeoutMS=10000)
    client.admin.command('ping')
    print("[OK] Connected to MongoDB")
except Exception as e:
    print(f"[ERROR] MongoDB connection failed: {e}")
    print("Please check your MONGO_URI in .env file")
    exit(1)

db = client["citizen_portal"]

services_col = db["services"]
categories_col = db["categories"]
officers_col = db["officers"]
ads_col = db["ads"]

services_col.delete_many({})
categories_col.delete_many({})
officers_col.delete_many({})
ads_col.delete_many({})

# seed a few categories
categories = [
    {"id":"cat_it","name":{"en":"IT & Digital","si":"තොරතුරු/ඩිජිටල්","ta":"தகவல் மற்றும் டிஜிடல්"},"ministry_ids":["ministry_it"]},
    {"id":"cat_health","name":{"en":"Health","si":"සෞඛ්‍යය","ta":"சுகாதாரம்"},"ministry_ids":["ministry_health"]},
    {"id":"cat_education","name":{"en":"Education","si":"අධ්‍යාපනය","ta":"கல்வி"},"ministry_ids":["ministry_education"]},
    {"id":"cat_transport","name":{"en":"Transport","si":"ප්‍රවාහනය","ta":"போக்குவரத்து"},"ministry_ids":["ministry_transport"]},
    {"id":"cat_land","name":{"en":"Land & Housing","si":"භූමි/නිවාස","ta":"நிலம் மற்றும் வீடுகள்"},"ministry_ids":["ministry_housing","ministry_land"]},
    {"id":"cat_elections","name":{"en":"Elections","si":"ඡන්දය","ta":"தேர்தल்"},"ministry_ids":["ministry_elections"]},
    {"id":"cat_water","name":{"en":"Water Supply","si":"ජල සපයාව","ta":"நீர் வழங்கல்"},"ministry_ids":["ministry_water"]},
    {"id":"cat_power","name":{"en":"Power & Energy","si":"බලශක්තി","ta":"மின்சக்தி"},"ministry_ids":["ministry_power"]},
    {"id":"cat_road_safety","name":{"en":"Road Safety","si":"මාර්ගවල ආරක්ෂාව","ta":"சாலை பாதுகாப்பு"},"ministry_ids":["ministry_road_safety"]},
    {"id":"cat_immigration","name":{"en":"Immigration","si":"සංක්‍රමණ","ta":"குடியேறுதல்"},"ministry_ids":["ministry_immigration"]},
    {"id":"cat_foreign","name":{"en":"Foreign Affairs","si":"විදේශ කටයුතු","ta":"வெளிநாட்டு விவகாரங்கள்"},"ministry_ids":["ministry_foreign"]},
    {"id":"cat_finance","name":{"en":"Finance","si":"මුදල්","ta":"நிதி"},"ministry_ids":["ministry_finance"]},
    {"id":"cat_labour","name":{"en":"Labour","si":"වැඩ","ta":"தொழிலாளர்"},"ministry_ids":["ministry_labour"]},
    {"id":"cat_justice","name":{"en":"Justice","si":"අධිකරණය","ta":"நீதிமன்றம்"},"ministry_ids":["ministry_justice"]},
    {"id":"cat_agriculture","name":{"en":"Agriculture","si":"කෘෂිකර්මාන්තය","ta":"விவசாயம்"},"ministry_ids":["ministry_agriculture"]},
    {"id":"cat_youth","name":{"en":"Youth Affairs","si":"තරුණ කටයුතු","ta":"இளைஞர் விவகாரங்கள்"},"ministry_ids":["ministry_youth"]},
    {"id":"cat_defence","name":{"en":"Defence","si":"ආරක්ෂණ","ta":"பாதுகாப்பு"},"ministry_ids":["ministry_defence"]},
    {"id":"cat_tourism","name":{"en":"Tourism","si":"සංචාරක","ta":"சுற்றுலா"},"ministry_ids":["ministry_tourism"]},
    {"id":"cat_trade","name":{"en":"Trade & Industry","si":"වෙළඳ උद්යෝගය","ta":"வர்த்தகம்"},"ministry_ids":["ministry_trade"]},
    {"id":"cat_environment","name":{"en":"Environment","si":"පරිසරය","ta":"சுற்றுச்சூழல்"},"ministry_ids":["ministry_environment"]},
]

categories_col.insert_many(categories)

# sample officers
officers_col.insert_many([
    {"id":"off_it_01","name":"Ms. Nayana Perera","role":"Director - Digital Services","ministry_id":"ministry_it","contact":{"email":"nayana@it.gov.lk","phone":"071-xxxxxxx"}},
    {"id":"off_health_01","name":"Dr. Suresh Kumar","role":"Chief Medical Officer","ministry_id":"ministry_health","contact":{"email":"suresh@health.gov.lk","phone":"011-yyyyyyy"}},
    {"id":"off_edu_01","name":"Mr. Rohan Silva","role":"Assistant Secretary - Education","ministry_id":"ministry_education","contact":{"email":"rohan@edu.gov.lk","phone":"071-zzzzzzz"}},
])

# sample ads/announcements
ads_col.insert_many([
    {"id":"ad_courses_01","title":"Free Digital Skills Course","body":"Enroll now for government digital skills training. Limited seats available.","link":"https://spacexp.edu.lk/courses","start":None,"end":None,"image":"/static/img/course-card.png"},
    {"id":"ad_exams_01","title":"Exam Results Portal","body":"Check your latest exam results online","link":"https://exam.gov.lk/results","start":None,"end":None},
    {"id":"ad_water_01","title":"New Water Connection Form","body":"Apply for new water connection with zero processing fees this month","link":"https://water.gov.lk/apply","start":None,"end":None},
])

# Extended services (20 ministries with sample questions)
docs = [
    {
        "id":"ministry_it",
        "category":"cat_it",
        "name":{"en":"Ministry of IT & Digital Affairs","si":"තොරතුරු ශිල්පය අමාත්‍යාංශය","ta":"தகவல் தொழில்நுட்ப அமைச்சு"},
        "subservices":[
            {"id":"it_cert","name":{"en":"IT Certificates","si":"අයිටී සහතික","ta":"ஐடி சொன்றிதழ்"},
            "questions":[
                {"q":{"en":"How to apply for an IT certificate?","si":"IT සහතිකය සඳහා ඉල්ලීම් කරන ආකාරය?","ta":"ஐடி சொன்றிதழுக்கு விண்ணப்பிப்பது எப்படி?"},
                "answer":{"en":"Fill online form and upload NIC.","si":"ඔන්ලයින් ප්‍රශ්න පත්‍ර පිරවුවා සුදු NIC උඩුගත කරන්න.","ta":"ஆன்மலனில் படிவத்தை நிரப்பி NIC ஐ பதிvicente."},
                "downloads":["/static/forms/it_cert_form.pdf"],
                "location":"https://maps.google.com/?q=Ministry+of+IT",
                "instructions":"Visit the digital portal, register and submit application."}
            ]}
        ]
    },
    {
        "id":"ministry_health",
        "category":"cat_health",
        "name":{"en":"Ministry of Health","si":"සෞඛ්‍ය අමාත්‍යාංශය","ta":"சுகாதார அமைச்சு"},
        "subservices":[
            {"id":"health_cert","name":{"en":"Health Certificates","si":"සෞඛ්‍ය සහතික","ta":"சுகாதார சொன்றிதழ்"},
            "questions":[
                {"q":{"en":"Where can I download exam results?","si":"විභාග ප්‍රතිඵල කොහි සිට බාගත කළ හැකිද?","ta":"பரீட்சை முடிவுகளை எங்கிருந்து பதிவிறக்க முடியும்?"},
                "answer":{"en":"Visit the health ministry portal and log in with your credentials.","si":"සෞඛ්‍ය අමාත්‍යාංශයේ ගිණුම වෙත ගිය විට ඔබේ අක්තපත හඳුන්වා දෙන්න.","ta":"சுகாதார அமைச்சு வெளியிட்ட இணையதளத்தைப் பார்வையிட்டு உங்கள் အကောင්ත నှိုးဝင်ပါ।"},
                "downloads":[],
                "location":"",
                "instructions":"Contact local health office for assistance."}
            ]}
        ]
    },
    {
        "id":"ministry_education",
        "category":"cat_education",
        "name":{"en":"Ministry of Education","si":"අධ්‍යාපන අමාත්‍යාංශය","ta":"கல்வி அமைச்சு"},
        "subservices":[
            {"id":"schools","name":{"en":"Schools","si":"පාසල්","ta":"பள்ளிகள்"},
            "questions":[
                {"q":{"en":"How to register a school?","si":"පාසලක් ලියා දිම්ශි කිරීම?","ta":"பள்ளிமை பதிவு செய்வது எப்படி?"},
                "answer":{"en":"Complete registration form and submit documents.","si":"ලියා දිම්ශි ප්‍රශ්න පත්‍ර පුරවා තල්ලුවිලින් දමන්න.","ta":"பதிவு படிவத்தை முற்றாக நிரப்பி ஆவணங்களை சமர்ப்பிக்கவும்."},
                "downloads":["/static/forms/school_reg.pdf"],
                "location":"https://maps.google.com/?q=Ministry+of+Education",
                "instructions":"Follow the guidelines on the education portal."}
            ]}
        ]
    },
    {
        "id":"ministry_transport",
        "category":"cat_transport",
        "name":{"en":"Ministry of Transport","si":"ප්‍රවාහන අමාත්‍යාංශය","ta":"போக்குவரத்து அமைச்சு"},
        "subservices":[
            {"id":"vehicle_reg","name":{"en":"Vehicle Registration","si":"වාහන ලියා දිම්ශි","ta":"வாகன பதிவு"},
            "questions":[
                {"q":{"en":"How to register a vehicle?","si":"වාහනයක් ලියා දිම්ශි කරන ආකාරය?","ta":"வாகனத்தை பதிவு செய்வது எப்படி?"},
                "answer":{"en":"Visit your nearest transport office with required documents.","si":"අවශ්‍ය ලේඛන සහිතව ඔබේ පිටුවා ගිය ප්‍රවාහන කාර්යාලයට පැමිණෙන්න.","ta":"தேவையான ஆவணங்களுடன் உங்கள் அருகிலுள்ள போக்குவரத்து அலுவலகத்திற்குச் செல்லவும்."},
                "downloads":["/static/forms/vehicle_reg.pdf"],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_housing",
        "category":"cat_land",
        "name":{"en":"Ministry of Housing","si":"නිවාස අමාත්‍යාංශය","ta":"வீட்டுப் பொறுப்பு அமைச்சு"},
        "subservices":[
            {"id":"permit","name":{"en":"Building Permits","si":"ඉඩම් සඳහා අවසර","ta":"கட்டடம் ஒப்புதல்"},
            "questions":[
                {"q":{"en":"How to apply for a building permit?","si":"ඉඩම් සඳහා ඇවසර ඉල්ලීම් කරන ආකාරය?","ta":"கட்டடம் அனுமதிக்கு விண்ணப்பிப்பது எப்படி?"},
                "answer":{"en":"Submit building permit application at your local municipal council.","si":"ඔබේ පිටුවා ගිය නගර සභාවේ ඉඩම් සඳහා ඇවසර ඉල්ලීම දමන්න.","ta":"உங்கள் உள்ளூர் நகரசபையில் கட்டடம் ஒப்புதல் விண்ணப்பத்தை சமர్ப்పிக்கவும்."},
                "downloads":["/static/forms/building_permit.pdf"],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_elections",
        "category":"cat_elections",
        "name":{"en":"Ministry of Elections","si":"ඡන්දය අමාත්‍යාංශය","ta":"தேர்தல் அமைச்சு"},
        "subservices":[
            {"id":"voter_reg","name":{"en":"Voter Registration","si":"ඡන්දදාතා ලියා දිම්ශි","ta":"வாக்காளர் பதிவு"},
            "questions":[
                {"q":{"en":"How to register as a voter?","si":"ඡන් freguතා ලෙස ලියා දිම්ශි කරන ආකාරය?","ta":"வாக்காளராக பதிவு செய்வது எப்படி?"},
                "answer":{"en":"Register online or at your nearest election office.","si":"ඔන්ලයිනින් ලියා දිම්ශි වන්න හෝ ඔබේ පිටුවා ගිය ඡන්ද කාර්යාලයට ගිහින් ලියා දිම්ශි වන්න.","ta":"ஆன்லைனில் பதிவு செய்யவும் அல்லது உங்கள் அருகிலுள்ள தேர்தல் அலுவலகத்திற்குச் செல்லவும்."},
                "downloads":[],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_water",
        "category":"cat_water",
        "name":{"en":"Ministry of Water Supply","si":"ජල සපයාව අමාත්‍යාංශය","ta":"நீர் வழங்கல் அமைச்சு"},
        "subservices":[
            {"id":"water_conn","name":{"en":"Water Connection","si":"ජල සংযෝගය","ta":"நீர் இணைப்பு"},
            "questions":[
                {"q":{"en":"How to get a new water connection?","si":"නැවුත් ජල සංයෝගයක් සඳහා අයදුම් කරන ආකාරය?","ta":"புதிய நீர் இணைப்பு பெற எப்படி?"},
                "answer":{"en":"Apply online or visit your local water supply office.","si":"ඔන්ලයිනින් අයදුම් කරන්න හෝ ඔබේ පිටුවා ගිය ජල සපයාව කාර්යාලයට පැමිණෙන්න.","ta":"ஆன்லைனில் விண்ணப்பிக்கவும் அல்லது உங்கள் உள்ளூர் நீர் வழங்கல் அலுவலகத்தைப் பார்வையிடவும்."},
                "downloads":["/static/forms/water_connection.pdf"],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_power",
        "category":"cat_power",
        "name":{"en":"Ministry of Power & Energy","si":"බලශක්තి අමාත්‍යාංශය","ta":"மின்சக்தி அமைச்சு"},
        "subservices":[
            {"id":"power_conn","name":{"en":"Power Connection","si":"බලශක්ති සංයෝගය","ta":"மின்சக்தி இணைப்பு"},
            "questions":[
                {"q":{"en":"How to apply for a new electricity connection?","si":"නැවුත් විද්‍යුත් සංයෝගය සඳහා අයදුම් කරන ආකාරය?","ta":"புதிய மின் இணைப்புக்கு விண்ணப்பிப்பது எப்படி?"},
                "answer":{"en":"Submit application at power ministry office with required documents.","si":"අවශ්‍ය ලේඛන සහිතව බලශක්ති අමාත්‍යාංශයේ කාර්යාලයට අයදුම් දමන්න.","ta":"தேவையான ஆவணங்களுடன் மின்சக்தி அமைச்சு அலுவலகத்তில் விண்ணப்பத்தை சமர్ப்பிக்கவும்."},
                "downloads":["/static/forms/power_connection.pdf"],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_road_safety",
        "category":"cat_road_safety",
        "name":{"en":"Ministry of Road Safety","si":"මාර්ගවල ආරක්ෂාව අමාත්‍යාංශය","ta":"சாலை பாதுகாப்பு அமைச்சு"},
        "subservices":[
            {"id":"road_complaint","name":{"en":"Road Complaints","si":"මාර්ගීය පැමිණිම්","ta":"சாலை புகார்"},
            "questions":[
                {"q":{"en":"Where to report a road safety complaint?","si":"සාල පිළිබඳ පැමිණිම් කොහි දැනුවත් කරන්න?","ta":"சாலை பாதுகாப்பு புகாரை எங்கு தெரிவிப்பது?"},
                "answer":{"en":"Report online through the road safety ministry website or call the hotline.","si":"සාල ආරක්ෂාව අමාත්‍යාංශයේ වෙබ්සයිටුවට ගිහින් ඔන්ලයිනින් පැමිණිම් කරන්න.","ta":"சாலை பாதுகாப்பு அமைச்சு இணையதளத்தின் மூலம் ஆன்லைனில் புகாரளிக்கவும்."},
                "downloads":[],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_immigration",
        "category":"cat_immigration",
        "name":{"en":"Ministry of Immigration","si":"සංක්‍රමණ අමාත්‍යාංශය","ta":"குடியேறுதல் அமைச்சு"},
        "subservices":[
            {"id":"passport","name":{"en":"Passport Services","si":"여권","ta":"செயற்பத்திரம்"},
            "questions":[
                {"q":{"en":"How to renew a passport?","si":"කරන හරස්තැගුල් ප්‍රතිස්ථාපනය කරන ආකාරය?","ta":"செயற்பத்திரம் புதிப்பது எப்படி?"},
                "answer":{"en":"Apply through immigration ministry office or online portal.","si":"සංක්‍රමණ අමාත්‍යාංශයේ කාර්යාලයට ගිහින් ඔන්ලයිනින් අයදුම් කරන්න.","ta":"குடியேறுதல் அமைச்சு அலுவலகத்தின் மூலம் ஆன்லைনில் விண்ணப்பிக்கவும்."},
                "downloads":["/static/forms/passport_form.pdf"],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_foreign",
        "category":"cat_foreign",
        "name":{"en":"Ministry of Foreign Affairs","si":"විදේශ කටයුතු අමාත්‍යාංශය","ta":"வெளிநாட்டு விவகாரங்கள் அமைச்சு"},
        "subservices":[
            {"id":"visa","name":{"en":"Visa Services","si":"වීසා","ta":"விசா"},
            "questions":[
                {"q":{"en":"How to apply for a visa?","si":"වීසා සඳහා අයදුම් කරන ආකාරය?","ta":"விசாவுக்கு விண்ணப்பிப்பது எப்படி?"},
                "answer":{"en":"Contact your nearest embassy or consulate for visa application.","si":"ඔබේ පිටුවා ගිය තුන්ඍිකවර හෝ නිලධරී හිමිකම් කාර්යාලයට යොමු කරන්න.","ta":"உங்கள் அருகிலுள்ள தூதரகம் அல்லது領事館த்தைத் தொடர்பு கொள்ளவும்."},
                "downloads":[],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_finance",
        "category":"cat_finance",
        "name":{"en":"Ministry of Finance","si":"මුදල් අමාත්‍යාංශය","ta":"நிதி அமைச்சு"},
        "subservices":[
            {"id":"tax","name":{"en":"Tax Services","si":"බදු සේවා","ta":"வரி சேவைகள்"},
            "questions":[
                {"q":{"en":"How to register for tax?","si":"බදුව සඳහා ලියා දිම්ශි කරන ආකාරය?","ta":"வரிக்கு பதிவு செய்வது எப்படி?"},
                "answer":{"en":"Register online through the tax ministry portal.","si":"බදු අමාත්‍යාංශයේ ඔන්ලයින් ගිණුම හරහා ලියා දිම්ශි වන්න.","ta":"வரி அமைச்சு ஆன்லைன் போர்ટலுக்கு பதிவு செய்யவும்."},
                "downloads":[],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_labour",
        "category":"cat_labour",
        "name":{"en":"Ministry of Labour","si":"ශ්‍රම අමාත්‍යාංශය","ta":"தொழிலாளர் அமைச்சு"},
        "subservices":[
            {"id":"labour_permit","name":{"en":"Labour Permits","si":"ශ්‍රම ඉඩසලාසි","ta":"தொழிலாளர் அனுமതிகள்"},
            "questions":[
                {"q":{"en":"How to get a labour permit?","si":"ශ්‍රම ඉඩසලාසි සඳහා අයදුම් කරන ආකාරය?","ta":"தொழிலாளர் அனுமதி பெற எப்படி?"},
                "answer":{"en":"Apply through labour ministry with required documents.","si":"අවශ්‍ය ලේඛන සහිතව ශ්‍රම අමාත්‍යාංශයට අයදුම් දමන්න.","ta":"தேவையான ஆவணங்களுடன் தொழிலாளர் அமைச்சு மூலம் விண்ணப்பிக்கவும்."},
                "downloads":["/static/forms/labour_permit.pdf"],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_justice",
        "category":"cat_justice",
        "name":{"en":"Ministry of Justice","si":"අධිකරණ අමාත්‍යාංශය","ta":"நீதிமன்ற அமைச்சு"},
        "subservices":[
            {"id":"legal_aid","name":{"en":"Legal Aid","si":"නීතිමය සහාය","ta":"சட்ட உதவி"},
            "questions":[
                {"q":{"en":"How to apply for legal aid?","si":"නීතිමය සහාය සඳහා අයදුම් කරන ආකාරය?","ta":"சட்ட உதவியுக்கு விண்ணப்பிப்பது எப்படி?"},
                "answer":{"en":"Contact your nearest legal aid office.","si":"ඔබේ පිටුවා ගිය නීතිමය සහාය කාර්යාලයට හෝ ඔන්ලයිනින් අයදුම් කරන්න.","ta":"உங்கள் அருகிலுள்ள சட்ட உதவி அலுவலகத்தைத் தொடர்பு கொள்ளவும்."},
                "downloads":[],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_agriculture",
        "category":"cat_agriculture",
        "name":{"en":"Ministry of Agriculture","si":"කෘෂිකර්මාන්ත අමාත්‍යාංශය","ta":"விவசாயம் அமைச்சு"},
        "subservices":[
            {"id":"farm_subsidy","name":{"en":"Farm Subsidies","si":"ගොවි සහතුකිරීම්","ta":"விவசாய மானியங்கள்"},
            "questions":[
                {"q":{"en":"How to apply for farm subsidy?","si":"ගොවි සහතුකිරීම් සඳහා අයදුම් කරන ආකාරය?","ta":"விவசாய மானியங்களுக்கு விண్ணப்पிப்பது எப்படி?"},
                "answer":{"en":"Apply through agriculture ministry with farm details.","si":"ගොවිබිම් තොරතුරු සහිතව කෘෂිකර්මාන්ත අමාත්‍යාංශයට අයදුම් දමන්න.","ta":"விவசாய விபரங்களுடன் விவசாயம் அமைச்சு மூலம் விண்ணப்பிக்கவும்."},
                "downloads":["/static/forms/farm_subsidy.pdf"],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_youth",
        "category":"cat_youth",
        "name":{"en":"Ministry of Youth Affairs","si":"තරුණ කටයුතු අමාත්‍යාංශය","ta":"இளைஞர் விவகாரங்கள் அமைச்சு"},
        "subservices":[
            {"id":"youth_prog","name":{"en":"Youth Programs","si":"තරුණ වැඩසටහන්","ta":"இளைஞர் திட்டங்கள்"},
            "questions":[
                {"q":{"en":"What youth programs are available?","si":"තරුණ වැඩසටහන් මොනවා ඇත්තේ?","ta":"கிடைக்கும் இளைஞர் திட்டங்கள் என்ன?"},
                "answer":{"en":"Check the ministry website for available youth programs and scholarships.","si":"තරුණ කටයුතු අමාත්‍යාංශයේ වෙබ්සයිටුවෙන් ඉතිරි වැඩසටහන් සහ ශිෂ්‍යත්ව බලන්න.","ta":"அமைச்சு இணையதளத்தில் கிடைக்கும் இளைஞர் திட்டங்கள் மற்றும் বৃத্திகள் பார்க்கவும்."},
                "downloads":[],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_defence",
        "category":"cat_defence",
        "name":{"en":"Ministry of Defence","si":"ආරක්ෂණ අමාත්‍යාංශය","ta":"பாதுகாப்பு அமைச்சு"},
        "subservices":[
            {"id":"military_recruit","name":{"en":"Military Recruitment","si":"හමුදා බඳවා ගැනීම","ta":"இராணுவ நியமனம்"},
            "questions":[
                {"q":{"en":"How to join the military?","si":"හමුදාවට ඇතුළු වන ආකාරය?","ta":"இராணுவத்தில் சேர எப்படி?"},
                "answer":{"en":"Check recruitment notices on ministry website and apply online.","si":"අමාත්‍යාංශයේ වෙබ්සයිටුවෙන් බඳවා ගැනීම් දැනුම්දීම් බලන්න.","ta":"அமைச்சு இணையதளத்தில் நியமன அறிவிப்புகள் பார்க்கவும்."},
                "downloads":[],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_tourism",
        "category":"cat_tourism",
        "name":{"en":"Ministry of Tourism","si":"සංචාරක අමාත්‍යාංශය","ta":"சுற்றுலா அமைச்சு"},
        "subservices":[
            {"id":"tourism_info","name":{"en":"Tourism Information","si":"සංචාරක තොරතුරු","ta":"சுற்றுலா தகவல்"},
            "questions":[
                {"q":{"en":"What are the best tourist destinations?","si":"හොඳ සංචාරක ස්‍ථාන මොනවා?","ta":"சிறந்த சுற்றுலா இடங்கள் என்ன?"},
                "answer":{"en":"Visit the tourism ministry website for information on tourist destinations.","si":"සංචාරක අමාත්‍යාංශයේ වෙබ්සයිටුවඩ ගිහින් සංචාරක ස්‍ථාන ගැන බලන්න.","ta":"சுற்றுலா அமைச்சு இணையதளத்தைப் பார்வையிடுங்கள்."},
                "downloads":[],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_trade",
        "category":"cat_trade",
        "name":{"en":"Ministry of Trade & Industry","si":"වෙළඳ උද්‍යෝගය අමාත්‍යාංශය","ta":"வர்த்தகம் மற்றும் தொழிற்சாலை அமைச்சு"},
        "subservices":[
            {"id":"business_reg","name":{"en":"Business Registration","si":"ව්‍යාපාර ලියා දිම්ශි","ta":"வணிக பதிவு"},
            "questions":[
                {"q":{"en":"How to register a business?","si":"ව්‍යාපාරයක් ලියා දිම්ශි කරන ආකාරය?","ta":"வணிகத்தை பதிவு செய்வது எப்படி?"},
                "answer":{"en":"Register online through the trade ministry business registration portal.","si":"වෙළඳ අමාත්‍යාංශයේ ඔන්ලයින් ගිණුම හරහා ලියා දිම්ශි වන්න.","ta":"வர்த்தகம் அமைச்சு ஆன்லைன் இணையத்தில் பதிவு செய்யவும்."},
                "downloads":["/static/forms/business_reg.pdf"],
                "location":"",
                "instructions":""}
            ]}
        ]
    },
    {
        "id":"ministry_environment",
        "category":"cat_environment",
        "name":{"en":"Ministry of Environment","si":"පරිසරය අමාත්‍යාංශය","ta":"சுற்றுச்சூழல் அமைச்சு"},
        "subservices":[
            {"id":"env_permit","name":{"en":"Environmental Permits","si":"පරිසර ඉඩසලාසි","ta":"சுற்றுச்சூழல் அனுமതிகள්"},
            "questions":[
                {"q":{"en":"How to get environmental clearance?","si":"පරිසර අනුමোදනය පිණිස ඉල්ලා සිටින ආකාරය?","ta":"சுற்றுச்சூழல் அனுமதி பெற எப்படி?"},
                "answer":{"en":"Apply for environmental clearance through the environment ministry.","si":"පරිසරය අමාත්‍යාංශය හරහා පරිසර අනුමොදනය සඳහා ඉල්ලා සිටින්න.","ta":"சுற்றுச்சூழல் அமைச்சு மூலம் சுற்றுச்சூழல் அனுமதির জন্য விண்ணப்பிக்கவும்."},
                "downloads":["/static/forms/env_clearance.pdf"],
                "location":"",
                "instructions":""}
            ]}
        ]
    }
]

services_col.insert_many(docs)
print(f"Seeded {services_col.count_documents({})} services")
print(f"Seeded {categories_col.count_documents({})} categories")
print(f"Seeded {officers_col.count_documents({})} officers")
print(f"Seeded {ads_col.count_documents({})} ads")
