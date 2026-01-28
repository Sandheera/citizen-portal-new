# Quick Start Guide

## Installation (5 minutes)

### Step 1: Setup Virtual Environment
```bash
cd c:\Users\janat\Desktop\citizen-portal-new
python -m venv venv
venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**If FAISS installation fails on Windows:**
- Edit `requirements.txt` and remove the FAISS line
- The app will auto-fallback to TF-IDF search

### Step 3: Seed Database
```bash
python seed_data.py
```

Expected output:
```
Seeded 20 services
Seeded 20 categories
Seeded 3 officers
Seeded 3 ads
```

### Step 4: Start Server
```bash
python app.py
```

Server runs at: **http://localhost:5000**

---

## First Run Checklist

✅ **Public Portal** - http://localhost:5000/
- Select a category from left sidebar
- Click a subservice
- Click a question to see the answer
- Click "Ask (AI)" for chat search

✅ **Admin Dashboard** - http://localhost:5000/admin
- Username: `admin`
- Password: `admin123`
- **IMPORTANT**: Click "Rebuild AI Index" to enable AI search
- View analytics charts
- Export CSV data

✅ **Service Management** - http://localhost:5000/admin/manage
- Add/edit services, categories, officers, ads
- After changes, rebuild AI index from admin dashboard

---

## Key Features to Test

### 1. Multi-Language Support
- Click English/Sinhala/தமிழ் buttons in sidebar
- All content switches language

### 2. AI Search
- Click "Ask (AI)" in main panel
- Type questions like "How to register a school?"
- Receive relevant answers with source links

### 3. Engagement Tracking
- Admin Dashboard shows:
  - Age group distribution
  - Job categories
  - Popular services
  - User desires/interests
  - Premium help suggestions

### 4. Ads System
- Ads appear in left sidebar
- Track clicks in admin dashboard

### 5. Progressive Profile
- Modal appears to gather user info step-by-step
- Non-intrusive, happens naturally

---

## MongoDB Connection

The `.env` file is pre-configured with:
```
MONGO_URI=mongodb+srv://sahashini:123@cluster0.uor202y.mongodb.net/citizen_portal
```

**To verify connection:**
```bash
python
>>> from pymongo import MongoClient
>>> from dotenv import load_dotenv
>>> import os
>>> load_dotenv()
>>> client = MongoClient(os.getenv("MONGO_URI"))
>>> print(client.server_info())  # Should show MongoDB version
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 5000 already in use | Change PORT in .env or kill process: `netstat -ano \| findstr :5000` |
| MongoDB connection error | Check internet, verify whitelist IP in Atlas |
| FAISS installation fails | Remove FAISS line from requirements.txt (uses fallback) |
| AI search not working | Click "Rebuild AI Index" in admin dashboard |
| Admin login fails | Check ADMIN_PWD in .env or use default |
| Static files not loading | Check static/ folder exists in correct location |

---

## File Structure Reference

```
citizen-portal-new/
├── app.py                    ← Main Flask application
├── seed_data.py              ← Populate database with sample data
├── requirements.txt          ← Python packages
├── .env                      ← Configuration (MongoDB, secrets)
├── README.md                 ← Full documentation
├── QUICKSTART.md             ← This file
├── templates/
│   ├── index.html            ← Public portal
│   ├── admin.html            ← Admin dashboard
│   └── manage.html           ← Service management
├── static/
│   ├── style.css             ← Styling
│   ├── script.js             ← Portal JavaScript
│   ├── admin.js              ← Admin JavaScript
│   └── manage.js             ← Management JavaScript
└── data/                     ← Created after first index build
    ├── faiss.index           ← Vector database
    └── faiss_meta.json       ← Document metadata
```

---

## Common Tasks

### Add a New Service
1. Go to http://localhost:5000/admin/manage
2. Click "Add New Service"
3. Fill form with service details
4. Go back to admin dashboard
5. Click "Rebuild AI Index"

### Export User Data
1. Admin Dashboard → "Export CSV"
2. Open CSV in Excel
3. Analyze engagement patterns

### Change Admin Password
1. Edit `.env`: `ADMIN_PWD=newpassword`
2. Delete or clear `admins` collection in MongoDB
3. Restart app (new password will be created)

### Enable HTTPS (Production)
1. Get SSL certificate (Let's Encrypt)
2. Use nginx as reverse proxy
3. Set `SESSION_COOKIE_SECURE=True` in app.py
4. Deploy to production server

---

## Sample Test Data Included

✅ 20 Government Ministries:
- IT & Digital
- Health
- Education
- Transport
- Housing & Land
- Elections
- Water Supply
- Power & Energy
- Road Safety
- Immigration
- Foreign Affairs
- Finance
- Labour
- Justice
- Agriculture
- Youth Affairs
- Defence
- Tourism
- Trade & Industry
- Environment

✅ 20 Service Categories

✅ Sample Officers (3)

✅ Sample Ads (3)

✅ ~60 FAQs with multilingual answers

---

## Next Steps

1. **Expand Content**: Add more services via admin panel
2. **Integrate LLM**: Add OpenAI API for natural language answers
3. **User Accounts**: Implement full authentication system
4. **Mobile App**: Build React Native companion app
5. **Deployment**: Deploy to Azure/AWS/PythonAnywhere
6. **Analytics**: Add Google Analytics or custom tracking
7. **Notifications**: Email/SMS notification system
8. **Scheduling**: Booking system for appointments

---

## Support

- Check error logs in terminal
- Inspect browser console (F12 → Console)
- Review README.md for detailed docs
- Check MongoDB Atlas for data verification

**Happy coding! 🚀**
