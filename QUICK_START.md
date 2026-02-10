# 🚀 Quick Start - Hierarchical Admin Panel

## Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB running
- Flask and dependencies installed

### Step 1: Verify Files
Check these files were updated:
```
✅ templates/manage.html      - New layout
✅ static/manage.js           - Tree navigation & forms  
✅ app.py                     - New API endpoint
✅ enhanced_seed_data.py      - Sample data
```

### Step 2: Load Sample Data (Optional)
If you have MongoDB running, load the sample hierarchical data:

```bash
# First, ensure MongoDB is running
# Then run:
python enhanced_seed_data.py
```

**Output should show:**
```
✓ Inserted 6 categories with 21 subcategories
✓ Inserted 7 enhanced officer profiles
✓ Inserted 7 enhanced advertisements
✅ Enhanced seed data loaded successfully!
```

### Step 3: Start the Application
```bash
python app.py
```

Then visit: **http://localhost:5000/admin/manage**

---

## 📊 What You'll See

### Left Sidebar - Category Tree
```
📂 Categories
[+ Add Category]

💻 IT & Digital Services
   └ 💻 Digital Certificates (5)
   └ 🎓 IT Training Programs (12)
   └ 🆘 Technical Support (8)

🏥 Health & Medical Services  
   └ 📋 Medical Certificates (7)
   └ 💉 Vaccination Programs (6)
   └ 🛡️ Health Insurance (9)
   └ 💪 Wellness Programs (5)

📚 Education & Training
   └ 🎒 School Enrollment (8)
   └ 📊 Exam Results (4)
   └ 🎓 Scholarships (15)
   └ 📜 Certificates (6)

... (and more)
```

### Right Panel - Services, Officers, Ads
- **Services**: Shows all government services with details
- **Officers**: Lists all officers with contact info & specializations  
- **Ads**: Displays announcements with dates & priority levels

---

## 🎯 How to Use

### Adding a New Category

1. Click **"+ Add Category"** button in sidebar
2. Fill out the form:
   - **Category ID**: Unique identifier (e.g., `cat_health`)
   - **Category Name**: Display name (e.g., "Health Services")
   - **Description**: What this category is about
   - **Icon**: Emoji (e.g., 🏥, 📚, 🚗)
   - **Color**: Hex code (e.g., #FF6B6B, #4ECDC4)
3. Click **Save**

### Adding Subcategories

1. **Click a category** in the tree to select it
2. Look for **+ Add Subcategory** (visible when category is expanded)
3. Fill out the form:
   - **Subcategory ID**: e.g., `subcat_vaccines`
   - **Name**: e.g., "Vaccination Programs"
   - **Description**: Details about this section
   - **Keywords**: Comma-separated (e.g., vaccine, health, immunization)
   - **Item Count**: How many items are in this section (e.g., 6)
4. Click **Save**

### Adding Officers

1. Click **"+ Add Officer"**
2. Fill all fields:
   - **ID**: Unique ID (e.g., `off_health_01`)
   - **Name**: Full name
   - **Role**: Job title (e.g., "Chief Medical Officer")
   - **Department**: Ministry/Department name
   - **Email**: Contact email
   - **Phone**: Contact number
   - **Specialization**: Area of expertise
   - **Bio**: Short description
3. Click **Save**

### Adding Announcements/Ads

1. Click **"+ Add Advertisement"**
2. Fill out:
   - **ID**: Unique identifier
   - **Title**: Announcement title
   - **Body**: Full description
   - **Type**: Select from dropdown
     - Promotion
     - Training Program
     - Announcement
     - Event
     - Important Notice
   - **Link**: URL to more info (optional)
   - **Target Audience**: Who should see this? (comma-separated)
     - Examples: youth, students, workers, seniors
   - **Start Date**: When to show (optional)
   - **End Date**: When to stop showing (optional)
   - **Priority**: How urgent?
     - Low, Medium, High, Urgent
3. Click **Save**

---

## 📋 Features by Category Type

### IT & Digital Services
- Digital Certificates
- IT Training Programs  
- Technical Support
- Cybersecurity Resources

### Health & Medical
- Medical Certificates
- Vaccination Programs
- Health Insurance Info
- Wellness Initiatives

### Education & Training
- School Enrollment
- Exam Results & Schedules
- Scholarships & Grants
- Educational Certificates

### Transport & Vehicles
- Vehicle Registration
- Driving Licenses
- Permits & Authorizations
- Public Transport Info

### Land & Housing
- Land Registration
- Housing Schemes
- Property Documents

### Elections & Voting
- Voter Registration
- Polling Information
- Candidate Information

---

## 🔍 Finding Content

### Using the Category Tree
1. **Browse**: Click category names to navigate
2. **Expand**: Click ▶ arrow to see subcategories
3. **Collapse**: Click ▼ arrow to hide subcategories
4. **Select**: Click category to highlight it (active state)

### Viewing Details
- **Each service** shows all subservices and questions count
- **Each officer** displays full contact information
- **Each ad** shows type, priority, dates, and target audience

---

## ✏️ Editing Content

To edit existing items:
1. Find the item in the panel
2. Click the **Delete** button if you want to remove it
3. To update: Add a new entry with the same ID (will update)

---

## 🗑️ Deleting Content

1. Find the item in any panel
2. Click the red **Delete** button
3. Confirm the deletion
4. Item will be removed from database

---

## 📱 Mobile Responsive

The system is designed to work on:
- ✅ Desktop (Full sidebar + panels)
- ✅ Tablet (Adjusted layout)
- ✅ Mobile (Stacked layout)

---

## 🔗 Database Collections

The system uses these MongoDB collections:

| Collection | Purpose | Example |
|-----------|---------|---------|
| **categories** | Main categories with subcategories | IT & Digital, Health, Education |
| **services** | Government services | Ministry of Health, MOT |
| **officers** | Staff directory | Dr. Suresh, Ms. Nayana |
| **ads** | Announcements & promotions | Free training, voting reminder |
| **engagements** | User activity tracking | Page views, clicks |

---

## ⚙️ Backend Endpoints

All data is managed through REST APIs:

```
GET/POST   /api/admin/categories
DELETE     /api/admin/categories?id=cat_id
POST       /api/admin/categories/add-subcategory

GET/POST   /api/admin/services
DELETE     /api/admin/services/{id}

GET/POST   /api/admin/officers
DELETE     /api/admin/officers?id=off_id

GET/POST   /api/admin/ads
DELETE     /api/admin/ads?id=ad_id
```

---

## 🎨 Customization

### Change Colors
In `templates/manage.html`, update CSS:
```css
/* Change primary blue to your color */
color: #0b3b8c;  /* Change this hex code */
```

### Change Icons
In the forms, use any emoji:
```
💻 🏥 📚 🚗 🏠 🗳️ 📋 👥 📢 🎯 ⭐ 🔗
```

### Add More Categories
Just click "+ Add Category" and create as many as you need!

---

## 🐛 Troubleshooting

### "No categories found"
- MongoDB might not be running
- Try loading enhanced_seed_data.py
- Check MongoDB connection in .env

### Form not submitting
- Fill all required fields (marked)
- Check browser console for errors
- Verify JSON format is correct

### Changes not saving
- Check MongoDB connection
- Verify network requests in browser DevTools
- Try refreshing the page

---

## 📚 Sample Data Included

Running `enhanced_seed_data.py` gives you:

**6 Categories** with **21 Subcategories**:
- IT & Digital (3 subcats, 25 items)
- Health (4 subcats, 27 items)
- Education (4 subcats, 33 items)
- Transport (4 subcats, 35 items)
- Land & Housing (3 subcats, 22 items)
- Elections (3 subcats, 13 items)

**7 Officer Profiles**:
- 2 from IT
- 2 from Health
- 2 from Education
- 1 from Transport

**7 Announcements**:
- Digital training course
- Exam results portal
- Water connection
- Health screening
- Voting reminder
- Driving license
- Housing scheme

---

## ✨ Pro Tips

1. **Use Icons Consistently** - Helps users quickly identify categories
2. **Keep Descriptions Short** - 1-2 sentences is ideal
3. **Update Dates Regularly** - Keep ads and announcements current
4. **Add Keywords** - Helps with search functionality
5. **Track Item Counts** - Helps users know what's available

---

## 🆘 Need Help?

1. Check STRUCTURE_DIAGRAM.txt for visual reference
2. Read HIERARCHICAL_CONTENT_GUIDE.md for detailed docs
3. Review enhanced_seed_data.py for example structure
4. Check browser console for error messages

Happy managing! 🎉
