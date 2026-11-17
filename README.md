# Sky Vision Group Consultancy — Django Web Platform

A production-ready, modular Django web application for **Sky Vision Group Consultancy**, providing recruitment, staffing, payroll, educational consultancy, and career services with a custom administrative management dashboard.

---

## 🏗 Architecture Overview

```
skyvision/
│
├── manage.py                   # Django CLI entrypoint
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── .env                        # Local environment variables
├── setup.bat                   # Automatic Windows CMD setup script
├── setup.ps1                   # Automatic PowerShell setup script
├── README.md                   # Documentation
│
├── config/                     # Core Project Settings & Master URLs
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/                       # Modular Django Applications
│   ├── core/                   # Public frontend views & page routing
│   ├── accounts/               # Custom Admin authentication & session management
│   ├── candidates/             # Job applications, resume upload, candidate management
│   ├── companies/              # Recruiter hiring requests & company enquiries
│   ├── internships/            # Internship applications & student enquiries
│   ├── placements/             # Placements tracking & job offers
│   ├── enquiries/              # General contact submissions, follow-ups & activity logs
│   ├── jobs/                   # Dynamic & scalable job openings model
│   └── dashboard/              # Custom Admin Dashboard views & metrics APIs
│
├── templates/                  # Django Template Architecture
│   ├── base.html               # Master layout extending all global CSS/JS
│   ├── includes/
│   │   ├── header.html         # Top utility bar (Contacts & Socials)
│   │   ├── navbar.html         # Main sticky navigation bar with active indicators
│   │   ├── footer.html         # Brand footer & floating contact widgets
│   │   └── modals.html         # Reusable modal popups (Apply, Job, Recruiter, Resume)
│   ├── pages/                  # All 19 Frontend Page Templates
│   └── dashboard/              # Custom Admin Dashboard & Login Templates
│
├── static/                     # Reorganized Static Assets
│   ├── css/
│   │   ├── global/             # Shared & layout stylesheets
│   │   ├── pages/              # Dedicated page stylesheets
│   │   └── admin/              # Admin dashboard styling
│   ├── js/
│   │   ├── global/             # Shared animations, sliders & core logic
│   │   ├── forms/              # Public form handlers (contact, apply, resume)
│   │   └── pages/              # Page-specific scripts
│   └── images/
│       ├── logo/               # Brand logos
│       ├── hero/               # Hero & background visuals
│       ├── blog/               # Blog banners
│       ├── team/               # Leadership & staff portraits
│       ├── services/           # Service iconography & graphics
│       └── general/            # Workshop & office imagery
│
├── media/                      # User Media & Resumes
│   └── uploads/
│       └── resumes/            # Secure candidate resumes (PDF, DOC, DOCX)
│
└── database/
    └── database.db             # Migrated SQLite Database with all records preserved
```

---

## 🚀 Quick Setup & Installation

### Option 1: Automatic Setup (Windows)

Double-click `setup.bat` or run in Command Prompt:
```cmd
setup.bat
```

Or in PowerShell:
```powershell
.\setup.ps1
```

---

### Option 2: Manual Setup

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows (CMD):
   venv\Scripts\activate
   # Windows (PowerShell):
   .\venv\Scripts\activate
   # Linux / macOS:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations:**
   ```bash
   python manage.py makemigrations accounts candidates companies internships placements enquiries jobs
   python manage.py migrate
   ```

4. **Start the Django Development Server:**
   ```bash
   python manage.py runserver
   ```

5. Open your browser:
   - **Main Website:** `http://127.0.0.1:8000/`
   - **Custom Admin Dashboard:** `http://127.0.0.1:8000/admin-panel/login/`
   - **Django Admin:** `http://127.0.0.1:8000/django-admin/`

---

## 📋 Available Frontend Routes

| Page | URL Path | View Name |
| :--- | :--- | :--- |
| **Home** | `/` | `core:home` |
| **About Us** | `/about/` | `core:about` |
| **About Company** | `/about/company/` | `core:about_company` |
| **Our Team** | `/about/team/` | `core:ourteam` |
| **CEO Message** | `/about/ceo/` | `core:ceo` |
| **Journey** | `/about/journey/` | `core:ourjourney` |
| **Services** | `/services/` | `core:services` |
| **Manpower Supply** | `/services/manpower-supply/` | `core:manpower_supply` |
| **Recruitment & Placement** | `/services/recruitment-placement/` | `core:recruitment_placement` |
| **Contract Staffing** | `/services/contract-staffing/` | `core:contract_staffing` |
| **Educational Consultancy** | `/services/educational-consultancy/` | `core:educational_consultancy` |
| **Payroll & Outsourcing** | `/services/payroll-outsourcing/` | `core:payroll_outsourcing` |
| **HR Support** | `/services/hr-support/` | `core:hr_support` |
| **Internship Programme** | `/services/internship/` | `core:internship` |
| **Careers & Counseling** | `/careers/` | `core:careers` |
| **Job Opportunities** | `/jobs/` | `core:jobs` |
| **Gallery** | `/gallery/` | `core:gallery` |
| **Blog** | `/blog/` | `core:blog` |
| **Contact Us** | `/contact/` | `core:contact` |

---

## 🛡 Security & Best Practices

- **CSRF & Session Protection:** Django session engine with `SESSION_COOKIE_HTTPONLY=True` and `SESSION_COOKIE_SAMESITE='Lax'`.
- **Password Security:** Multi-algorithm verification supporting PBKDF2, Argon2, and automatic upgrades from legacy hashes.
- **Upload Validation:** UUID-based storage in `media/uploads/resumes/` with strict format (PDF, DOC, DOCX) and 10 MB size limits.
- **Rate Limiting:** IP-based brute-force prevention on authentication endpoints (5 attempts per 15-minute window).
- **Environment Isolation:** Secrets, keys, and database configurations managed via `.env` file using `django-environ`.
