# Citizen Services Portal - Task 07 (AI-Enabled)

A comprehensive Flask-based government services portal with AI-powered search, multi-language support, and admin dashboard.

## Features

- **Public Portal**: Browse 20+ government service categories with multilingual support (English, Sinhala, தமிழ்)
- **AI Chat Search**: Vector-based semantic search using FAISS embeddings and SentenceTransformer
- **Progressive Profile**: Step-by-step user profiling without friction
- **Admin Dashboard**: Comprehensive analytics with Charts.js
- **Service Management**: CRUD operations for services, categories, officers, and advertisements
- **Engagement Tracking**: Track user interactions, demographics, and interests
- **CSV Export**: Export analytics data for further analysis

## Project Structure

```
citizen-portal/
├── app.py                    # Flask backend with all routes
├── seed_data.py              # MongoDB data seeding script
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── templates/
│   ├── index.html           # Public portal UI
│   ├── admin.html           # Admin dashboard
│   └── manage.html          # Service management interface
├── static/
│   ├── style.css            # Main stylesheet
│   ├── script.js            # Public portal JavaScript
│   ├── admin.js             # Admin dashboard JavaScript
│   └── manage.js            # Management interface JavaScript
└── data/                    # FAISS index and embeddings (auto-created)
    ├── faiss.index          # Vector database
    └── faiss_meta.json      # Document metadata
```

## Setup & Installation

### 1. Prerequisites
- Python 3.8+
- MongoDB Atlas account (free tier available)
- Virtual environment (optional but recommended)

### 2. Clone/Setup Project
```bash
cd c:\Users\janat\Desktop\citizen-portal-new
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: If FAISS fails to install on your dev machine (common on Windows):
- Remove `faiss-cpu==1.7.4` from requirements.txt
- The app will use a TF-IDF fallback (slower but functional)

### 4. Configure Environment Variables
The `.env` file is already configured with:
- MongoDB Atlas connection string (provided)
- Flask secret key
- Admin password
- Embedding model

**Important**: Update `.env` for production:
```
MONGO_URI=mongodb+srv://your-user:your-pass@your-cluster.mongodb.net/citizen_portal?retryWrites=true&w=majority
FLASK_SECRET=your-secure-random-string
ADMIN_PWD=your-strong-password
```

### 5. Seed Initial Data
```bash
python seed_data.py
```

This populates:
- 20 government ministries with 1-2 subservices each
- 20 service categories
- 3 sample officers
- 3 sample advertisements

### 6. Run the Application
```bash
python app.py
```

Server starts at: http://localhost:5000

## Usage

### Public Portal
1. **Homepage**: http://localhost:5000/
2. Click a **Category** on the left sidebar
3. Select a **Subservice**
4. Click a **Question** to view the answer
5. Use **"Ask (AI)"** button for semantic search with chat interface

### Admin Dashboard
1. **Login**: http://localhost:5000/admin
2. Default credentials: `admin` / `admin123`
3. View analytics and engagement insights
4. **Important**: Click **"Rebuild AI Index"** after modifying services
5. Export engagement data as CSV

### Service Management
1. **Admin only**: http://localhost:5000/admin/manage
2. Add/Edit/Delete services, categories, officers, and advertisements

## API Endpoints

### Public APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/services` | Get all services |
| GET | `/api/service/<id>` | Get specific service |
| GET | `/api/categories` | Get all categories |
| GET | `/api/ads` | Get advertisements |
| POST | `/api/engagement` | Log user engagement |
| POST | `/api/ai/search` | AI-powered semantic search |
| GET | `/api/search/autosuggest` | Typeahead search |
| POST | `/api/profile/step` | Save profile data (progressive) |

### Admin APIs (Require Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/build_index` | Rebuild FAISS vector index |
| GET | `/api/admin/insights` | Get analytics data |
| GET | `/api/admin/engagements` | Get recent engagements |
| GET | `/api/admin/export_csv` | Export data as CSV |
| GET/POST/DELETE | `/api/admin/services` | Manage services |
| GET/POST/DELETE | `/api/admin/categories` | Manage categories |
| GET/POST/DELETE | `/api/admin/officers` | Manage officers |
| GET/POST/DELETE | `/api/admin/ads` | Manage advertisements |

## Key Components

### Backend (Flask + MongoDB)

**Collections**:
- `services`: Ministries with subservices and questions
- `categories`: Service categories and groupings
- `officers`: Government officer metadata
- `ads`: Advertisements and announcements
- `engagements`: User interaction logs
- `users`: Progressive profile data
- `admins`: Admin credentials (bcrypt hashed)

**Features**:
- Bcrypt password hashing for admin accounts
- FAISS vector indexing for fast semantic search
- SentenceTransformer embeddings (all-MiniLM-L6-v2)
- MongoDB aggregation pipeline for analytics
- Session-based admin authentication

### Frontend

**Technologies**:
- Vanilla JavaScript (no frameworks)
- CSS3 with responsive design
- Chart.js for admin analytics
- HTML5 semantic markup

**Responsive Layout**:
- 4-column desktop: Sidebar | Middle | Content | Chat
- Mobile-optimized with flexbox

## AI/Vector Search Details

### How It Works

1. **Indexing**: 
   - Flattens all service/subservice/question documents
   - Creates embeddings using `sentence-transformers/all-MiniLM-L6-v2`
   - Stores in FAISS with metadata (384-dim vectors)
   - Saves index to `data/faiss.index` and metadata to `data/faiss_meta.json`

2. **Searching**:
   - User query → embedding → cosine similarity search
   - Returns top 5 most similar documents
   - Concatenates answers for response
   - Can integrate LLM (GPT) for natural language generation

3. **Fallback**:
   - If FAISS unavailable: linear numpy scan (slower)
   - Same results, slower performance

### Rebuild Index
After modifying services in admin panel:
```
Admin Dashboard → "Rebuild AI Index" button
```

Or via API:
```bash
curl -X POST http://localhost:5000/api/admin/build_index \
  -H "Authorization: Bearer <session>"
```

## Testing Queries

Test the AI chat with these sample queries:
1. "How to apply for an IT certificate?"
2. "Where can I download exam results?"
3. "How to register a school?"
4. "How to change my NIC details?"
5. "How to apply for a building permit?"
6. "What is the process for passport renewal?"
7. "How can I get water connection?"
8. "Where to report a road safety complaint?"
9. "How to register a business?"
10. "What training courses are available?"

## Security Considerations

### Current (Development)
- Session-based authentication
- Bcrypt password hashing
- CORS enabled for development

### Production Checklist
- [ ] Use HTTPS only (`SESSION_COOKIE_SECURE = True`)
- [ ] Enable `SESSION_COOKIE_HTTPONLY = True`
- [ ] Use Flask-Login with secure session management
- [ ] Deploy behind nginx reverse proxy
- [ ] Set strong `FLASK_SECRET` (use `secrets.token_hex(32)`)
- [ ] Update admin password
- [ ] Whitelist MongoDB IP address
- [ ] Implement rate limiting on public APIs
- [ ] Add input validation and sanitization
- [ ] Use environment variables for secrets
- [ ] Enable MongoDB authentication
- [ ] Add logging and monitoring
- [ ] Set up automated backups

## Deployment

### Azure App Service
```bash
# Create deployment package
zip -r app.zip . -x "*.git*" "venv/*" ".env"

# Deploy
az webapp up --name citizen-portal-app --resource-group myResourceGroup
```

### PythonAnywhere
1. Upload files to account
2. Set up virtual environment
3. Configure WSGI file
4. Set environment variables in Web config
5. Reload web app

### Local Server
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Troubleshooting

### FAISS Installation Fails
- Remove `faiss-cpu` from requirements.txt
- App will use numpy fallback (slower but works)

### MongoDB Connection Error
- Verify `.env` has correct `MONGO_URI`
- Check whitelist IP in MongoDB Atlas
- Ensure network connectivity

### AI Search Returns No Results
- Click **"Rebuild AI Index"** in admin dashboard
- Ensure services are properly seeded
- Check `data/faiss.index` exists

### Admin Can't Login
- Default: `admin` / `admin123`
- Check `.env` `ADMIN_PWD` value
- Clear browser cookies and try again

## Future Enhancements

1. **LLM Integration**: Use OpenAI GPT to generate human-friendly answers
2. **Recommendation Engine**: ML-based service recommendations
3. **User Accounts**: Full login/registration system
4. **Notifications**: Email/SMS notifications for application status
5. **File Upload**: Document submission for applications
6. **Multi-language Localization**: Complete translations
7. **Mobile App**: React Native companion app
8. **Scheduling**: Book appointments with government offices
9. **Payment Integration**: Online payment for services
10. **Analytics Dashboard**: Advanced reporting and insights

## Support & Contact

For issues or questions:
- Check troubleshooting section above
- Review Flask error logs
- Inspect browser console (F12)
- Check MongoDB Atlas status

## License

Development project for AI-enabled citizen services portal.

---

**Created**: January 2026
**Version**: 1.0.0
**Status**: Production Ready (with security updates)
