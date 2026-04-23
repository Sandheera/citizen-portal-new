# CitizenPortal Project Structure

## Directory Organization

```
citizen-portal-new/
├── backend/                    # Flask backend server
│   ├── app.py                 # Main Flask application
│   ├── api/                   # API modules
│   ├── .env                   # Environment variables
│   ├── requirements.txt       # Python dependencies
│   ├── data/                  # FAISS index and metadata (generated)
│   ├── __pycache__/           # Python cache
│   ├── *.py                   # Helper/seed scripts
│   │   ├── check_app.py
│   │   ├── diagnostic.py
│   │   ├── seed_data.py
│   │   ├── complete_seed.py
│   │   ├── verify_files.py
│   │   └── ... (other utilities)
│   └── config/                # Configuration files (if needed)
│
├── frontend/                  # Frontend files
│   ├── static/                # Static assets
│   │   ├── style.css         # Stylesheet
│   │   ├── script.js         # Main JavaScript
│   │   ├── admin.js          # Admin panel JS
│   │   └── manage.js         # Manage page JS
│   │
│   └── templates/             # HTML templates
│       ├── index.html        # Home page
│       ├── login.html        # Login/Registration page
│       ├── admin.html        # Admin dashboard
│       ├── dashboard.html    # Dashboard
│       ├── manage.html       # Manage page
│       ├── profile.html      # User profile
│       └── shop.html         # Shop page
│
├── .git/                      # Git repository
├── .gitignore                 # Git ignore rules
├── README.md                  # Main documentation
├── QUICK_START.md            # Quick start guide
└── ... (other documentation files)
```

## Running the Application

### From the Backend Folder (Recommended)
```bash
cd backend
python app.py
```

### From the Project Root
```bash
cd backend
python app.py
```

**Note:** The Flask app references frontend resources at `../frontend/static` and `../frontend/templates`, so it expects to be run from the backend folder or with the correct working directory.

## Key Changes Made

1. **Backend Directory** - Contains all Python files:
   - Main application (app.py)
   - API modules
   - Database configuration
   - Helper scripts and seed data
   - Environment configuration

2. **Frontend Directory** - Contains all UI files:
   - Static assets (CSS, JavaScript)
   - HTML templates

3. **Flask Configuration** - Updated to reference:
   - `static_folder="../frontend/static"`
   - `template_folder="../frontend/templates"`

## Development Workflow

### Backend Development
```bash
cd backend
python -m pip install -r requirements.txt
python app.py
```

### Frontend Development
- Edit files in `frontend/templates/` for HTML
- Edit files in `frontend/static/` for CSS and JavaScript
- Changes reflect on page reload

## Docker Deployment (Optional Future)
This structure is ideal for containerization:
- Backend runs in its own container
- Frontend can be served separately if needed
- Clear separation of concerns

## Environment Setup
- Copy `.env` from backend folder or create one with:
  ```
  FLASK_SECRET=your-secret-key
  MONGO_URI=your-mongodb-connection
  ```

---

**Last Updated:** 2026-04-22
