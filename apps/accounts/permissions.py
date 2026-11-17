"""
Single source of truth for Role & Permission registry in Sky Vision Consultancy.
Maps sidebar modules, allowed actions, default roles permissions, and complete URL permission mappings.
"""
import re

# Modules definition: (module_key, label, section, [allowed_actions])
MODULES = [
    # MAIN
    ("dashboard", "Dashboard Overview", "MAIN", ["view", "export"]),
    ("enquiries", "Enquiries Management", "MAIN", ["view", "edit", "delete", "export"]),
    ("analytics", "Analytics & Insights", "MAIN", ["view", "export"]),
    ("registrations", "Registrations & Approvals", "MAIN", ["view", "approve", "delete", "export"]),

    # USERS & MANAGEMENT
    ("candidates", "Candidate Directory", "USERS & MANAGEMENT", ["view", "add", "edit", "delete", "export"]),
    ("employers", "Employer Directory", "USERS & MANAGEMENT", ["view", "add", "edit", "delete", "export"]),
    ("internships", "Internships Hub", "USERS & MANAGEMENT", ["view", "add", "edit", "delete", "export"]),
    ("staff", "Staff Management", "USERS & MANAGEMENT", ["view", "add", "edit", "delete", "export", "view_salary"]),
    ("roles", "Role & Permissions", "USERS & MANAGEMENT", ["view", "add", "edit", "delete"]),
    ("admin_users", "Admin Users Management", "USERS & MANAGEMENT", ["view", "add", "edit", "delete"]),

    # JOB MANAGEMENT
    ("job_postings", "Job Postings", "JOB MANAGEMENT", ["view", "add", "edit", "delete", "export"]),
    ("job_categories", "Job Categories", "JOB MANAGEMENT", ["view", "add", "edit", "delete"]),
    ("job_approvals", "Job Approvals", "JOB MANAGEMENT", ["view", "approve", "delete", "export"]),
    ("applications", "Job Applications", "JOB MANAGEMENT", ["view", "approve", "delete", "export"]),

    # PLACEMENTS
    ("shortlisted", "Shortlisted Candidates", "PLACEMENTS", ["view", "edit", "delete", "export"]),
    ("interviews", "Interview Schedules", "PLACEMENTS", ["view", "add", "edit", "delete", "export"]),
    ("selections", "Candidate Selections", "PLACEMENTS", ["view", "edit", "delete", "export"]),
    ("offer_letters", "Offer Letters", "PLACEMENTS", ["view", "add", "edit", "delete", "export", "approve"]),
    ("joinings", "Candidate Joinings", "PLACEMENTS", ["view", "add", "edit", "delete", "export"]),

    # BILLING & FINANCE
    ("ledger", "Accounting Ledger", "BILLING & FINANCE", ["view", "add", "edit", "delete", "export"]),
    ("invoices", "Invoices", "BILLING & FINANCE", ["view", "add", "edit", "export"]),
    ("payments", "Payments & Collections", "BILLING & FINANCE", ["view", "add", "edit", "delete", "export"]),
    ("commission", "Commission Management", "BILLING & FINANCE", ["view", "add", "edit", "export"]),

    # EMAIL & NOTIFICATIONS
    ("comm_compose", "Compose Message", "EMAIL & NOTIFICATIONS", ["view", "add"]),
    ("comm_history", "Communication Sent History", "EMAIL & NOTIFICATIONS", ["view", "delete", "export"]),
    ("comm_templates", "Message Templates", "EMAIL & NOTIFICATIONS", ["view", "add", "edit", "delete"]),
    ("comm_settings", "Delivery Settings", "EMAIL & NOTIFICATIONS", ["view", "edit"]),

    # REPORTS & SETTINGS
    ("reports", "System Reports", "REPORTS & SETTINGS", ["view", "export"]),
    ("activity_log", "Activity & Audit Logs", "REPORTS & SETTINGS", ["view", "export"]),
    ("system_settings", "System Settings", "REPORTS & SETTINGS", ["view", "edit"]),
    ("website_management", "Website Content Management", "REPORTS & SETTINGS", ["view", "edit"]),
]

ACTION_LABELS = {
    "view": "View / Read",
    "add": "Create / Add",
    "edit": "Edit / Update",
    "delete": "Delete / Remove",
    "export": "Export Data",
    "approve": "Approve / Reject",
    "view_salary": "View Salary / Bank Data",
}

def get_all_permission_codes():
    """Return all valid permission codes."""
    codes = []
    for mod_key, _, _, actions in MODULES:
        for action in actions:
            codes.append(f"{mod_key}.{action}")
    return codes

def get_modules_by_section():
    """Group modules by their sidebar sections for UI rendering."""
    sections = {}
    for mod_key, label, section, actions in MODULES:
        if section not in sections:
            sections[section] = []
        sections[section].append({
            "key": mod_key,
            "label": label,
            "actions": actions,
            "permission_codes": [f"{mod_key}.{act}" for act in actions]
        })
    return sections

# Default permissions assigned to seed roles
DEFAULT_ROLES_PERMISSIONS = {
    "Super Admin": {
        "description": "Full unconstrained administrative access across all modules, settings, and role management.",
        "is_super": True,
        "is_system": True,
        "permissions": get_all_permission_codes(),
    },
    "Admin": {
        "description": "General administrator with access to operational modules except system role customization and confidential salaries.",
        "is_super": False,
        "is_system": True,
        "permissions": [
            code for code in get_all_permission_codes()
            if not code.startswith("roles.") and code != "staff.view_salary"
        ],
    },
    "HR Manager": {
        "description": "Human Resources manager handling staff records, salaries, candidate registrations and interviews.",
        "is_super": False,
        "is_system": True,
        "permissions": [
            "dashboard.view",
            "staff.view", "staff.add", "staff.edit", "staff.delete", "staff.export", "staff.view_salary",
            "candidates.view", "candidates.add", "candidates.edit", "candidates.export",
            "registrations.view", "registrations.approve", "registrations.export",
            "shortlisted.view", "shortlisted.edit",
            "interviews.view", "interviews.add", "interviews.edit", "interviews.export",
            "selections.view", "selections.edit",
            "offer_letters.view", "offer_letters.add", "offer_letters.export",
            "joinings.view", "joinings.add", "joinings.edit",
            "comm_compose.view", "comm_compose.add",
            "comm_history.view",
            "reports.view", "reports.export",
        ],
    },
    "Recruiter": {
        "description": "Recruitment team member screening candidates, tracking employer jobs, applications and pipeline stages.",
        "is_super": False,
        "is_system": True,
        "permissions": [
            "dashboard.view",
            "candidates.view", "candidates.add", "candidates.edit", "candidates.export",
            "employers.view",
            "job_postings.view", "job_postings.add", "job_postings.edit",
            "job_categories.view",
            "applications.view", "applications.approve", "applications.export",
            "shortlisted.view", "shortlisted.edit",
            "interviews.view", "interviews.add", "interviews.edit",
            "selections.view", "selections.edit",
            "offer_letters.view", "offer_letters.add",
            "joinings.view",
            "comm_compose.view", "comm_compose.add",
            "comm_history.view",
        ],
    },
    "Accountant": {
        "description": "Finance & accounting specialist managing ledger books, invoice vouchers, collections and candidate commissions.",
        "is_super": False,
        "is_system": True,
        "permissions": [
            "dashboard.view", "dashboard.export",
            "ledger.view", "ledger.add", "ledger.edit", "ledger.delete", "ledger.export",
            "invoices.view", "invoices.add", "invoices.edit", "invoices.export",
            "payments.view", "payments.add", "payments.edit", "payments.delete", "payments.export",
            "commission.view", "commission.add", "commission.edit", "commission.export",
            "staff.view", "staff.view_salary", "staff.export",
            "reports.view", "reports.export",
        ],
    },
    "Content Manager": {
        "description": "Website administrator managing public portal content, banners, testimonials, blogs and gallery.",
        "is_super": False,
        "is_system": True,
        "permissions": [
            "dashboard.view",
            "website_management.view", "website_management.edit",
            "job_categories.view", "job_categories.add", "job_categories.edit",
        ],
    },
    "Viewer": {
        "description": "Read-only audit access across key modules without editing or deletion privileges.",
        "is_super": False,
        "is_system": True,
        "permissions": [
            "dashboard.view",
            "enquiries.view",
            "analytics.view",
            "registrations.view",
            "candidates.view",
            "employers.view",
            "internships.view",
            "job_postings.view",
            "job_categories.view",
            "applications.view",
            "shortlisted.view",
            "interviews.view",
            "selections.view",
            "joinings.view",
            "reports.view",
        ],
    },
}

# Complete URL Permission Map:
# Format: (module_key, pattern_regex, method, permission_code)
# Covers ALL methods (GET, POST, PUT, DELETE) and both web & API endpoints.
URL_PERMISSION_MAP = [
    # ==========================
    # 1. DASHBOARD
    # ==========================
    ("dashboard", r"^/admin-panel/dashboard/?$", "GET", "dashboard.view"),
    ("dashboard", r"^/api/admin/dashboard-stats/?$", "GET", "dashboard.view"),
    ("dashboard", r"^/api/admin/topbar-counts/?$", "GET", "dashboard.view"),

    # ==========================
    # 2. ENQUIRIES & CONTACTS
    # ==========================
    ("enquiries", r"^/admin-panel/enquiries", "GET", "enquiries.view"),
    ("enquiries", r"^/admin-panel/followups", "GET", "enquiries.view"),
    ("enquiries", r"^/api/enquiries/?$", "GET", "enquiries.view"),
    ("enquiries", r"^/api/enquiries/counts/?$", "GET", "enquiries.view"),
    ("enquiries", r"^/api/enquiries/export/?$", "GET", "enquiries.export"),
    ("enquiries", r"^/api/enquiry/mark-read/?$", "POST", "enquiries.edit"),
    ("enquiries", r"^/api/enquiry/mark-unread/?$", "POST", "enquiries.edit"),
    ("enquiries", r"^/api/enquiry/bulk-status/?$", "POST", "enquiries.edit"),
    ("enquiries", r"^/api/enquiry/mark-spam/?$", "POST", "enquiries.edit"),
    ("enquiries", r"^/api/enquiry/restore/?$", "POST", "enquiries.edit"),
    ("enquiries", r"^/api/contacts/?$", "GET", "enquiries.view"),
    ("enquiries", r"^/api/contact/\d+/?$", "GET", "enquiries.view"),
    ("enquiries", r"^/api/contact/\d+/?$", "DELETE", "enquiries.delete"),
    ("enquiries", r"^/api/follow-ups/?$", "GET", "enquiries.view"),
    ("enquiries", r"^/api/follow-ups/?$", "POST", "enquiries.edit"),
    ("enquiries", r"^/api/follow-up/\d+/?$", "DELETE", "enquiries.delete"),
    ("enquiries", r"^/api/company-enquiries/?$", "GET", "enquiries.view"),
    ("enquiries", r"^/api/company-enquiry/\d+/?$", "GET", "enquiries.view"),
    ("enquiries", r"^/api/company-enquiry/\d+/?$", "DELETE", "enquiries.delete"),
    ("enquiries", r"^/api/internship-enquiries/?$", "GET", "enquiries.view"),
    ("enquiries", r"^/api/internship-enquiry/\d+/?$", "GET", "enquiries.view"),
    ("enquiries", r"^/api/internship-enquiry/\d+/?$", "DELETE", "enquiries.delete"),

    # ==========================
    # 3. ANALYTICS
    # ==========================
    ("analytics", r"^/admin-panel/reports/candidate/?$", "GET", "analytics.view"),

    # ==========================
    # 4. REGISTRATIONS & APPROVALS
    # ==========================
    ("registrations", r"^/admin-panel/registrations", "GET", "registrations.view"),
    ("registrations", r"^/api/admin/candidate-registrations/?$", "GET", "registrations.view"),
    ("registrations", r"^/api/admin/candidate-registrations/\d+/?$", "GET", "registrations.view"),
    ("registrations", r"^/api/admin/candidate-registrations/\d+/approve/?$", "POST", "registrations.approve"),
    ("registrations", r"^/api/admin/candidate-registrations/\d+/reject/?$", "POST", "registrations.approve"),
    ("registrations", r"^/api/admin/employer-registrations/?$", "GET", "registrations.view"),
    ("registrations", r"^/api/admin/employer-registrations/\d+/?$", "GET", "registrations.view"),
    ("registrations", r"^/api/admin/employer-registrations/\d+/approve/?$", "POST", "registrations.approve"),
    ("registrations", r"^/api/admin/employer-registrations/\d+/reject/?$", "POST", "registrations.approve"),
    ("registrations", r"^/api/admin/employer-registrations/\d+/suspend/?$", "POST", "registrations.approve"),
    ("registrations", r"^/api/admin/registrations", "GET", "registrations.view"),
    ("registrations", r"^/api/admin/registrations/summary/?$", "GET", "registrations.view"),
    ("registrations", r"^/api/admin/registrations/export/?$", "GET", "registrations.export"),
    ("registrations", r"^/api/admin/registrations/bulk-action/?$", "POST", "registrations.approve"),

    # ==========================
    # 5. CANDIDATE DIRECTORY & RESUMES
    # ==========================
    ("candidates", r"^/admin-panel/candidates/add/?$", "GET", "candidates.add"),
    ("candidates", r"^/admin-panel/candidates/?$", "GET", "candidates.view"),
    ("candidates", r"^/admin-panel/candidates/all/?$", "GET", "candidates.view"),
    ("candidates", r"^/admin-panel/users/candidates/?$", "GET", "candidates.view"),
    ("candidates", r"^/api/applicants/?$", "GET", "candidates.view"),
    ("candidates", r"^/api/admin/applicants/?$", "POST", "candidates.add"),
    ("candidates", r"^/api/candidates/create/?$", "POST", "candidates.add"),
    ("candidates", r"^/api/applicant/\d+/?$", "GET", "candidates.view"),
    ("candidates", r"^/api/applicant/\d+/?$", "POST", "candidates.edit"),
    ("candidates", r"^/api/applicant/\d+/?$", "PUT", "candidates.edit"),
    ("candidates", r"^/api/applicant/\d+/?$", "DELETE", "candidates.delete"),
    ("candidates", r"^/api/resumes/?$", "GET", "candidates.view"),
    ("candidates", r"^/api/resume/\d+/?$", "GET", "candidates.view"),
    ("candidates", r"^/api/resume/\d+/?$", "DELETE", "candidates.delete"),

    # ==========================
    # 6. EMPLOYERS & CONTACTS
    # ==========================
    ("employers", r"^/admin-panel/companies/add/?$", "GET", "employers.add"),
    ("employers", r"^/admin-panel/companies/?$", "GET", "employers.view"),
    ("employers", r"^/admin-panel/companies/all/?$", "GET", "employers.view"),
    ("employers", r"^/api/companies/?$", "GET", "employers.view"),
    ("employers", r"^/api/companies/?$", "POST", "employers.add"),
    ("employers", r"^/api/company/\d+/?$", "GET", "employers.view"),
    ("employers", r"^/api/company/\d+/?$", "POST", "employers.edit"),
    ("employers", r"^/api/company/\d+/?$", "PUT", "employers.edit"),
    ("employers", r"^/api/company/\d+/?$", "DELETE", "employers.delete"),
    ("employers", r"^/api/company-contacts/?$", "GET", "employers.view"),
    ("employers", r"^/api/company-contacts/?$", "POST", "employers.add"),
    ("employers", r"^/api/company-contact/\d+/?$", "GET", "employers.view"),
    ("employers", r"^/api/company-contact/\d+/?$", "PUT", "employers.edit"),
    ("employers", r"^/api/company-contact/\d+/?$", "DELETE", "employers.delete"),

    # ==========================
    # 7. INTERNSHIPS
    # ==========================
    ("internships", r"^/admin-panel/internships/add/?$", "GET", "internships.add"),
    ("internships", r"^/admin-panel/internships", "GET", "internships.view"),
    ("internships", r"^/api/internships/?$", "GET", "internships.view"),
    ("internships", r"^/api/internships/?$", "POST", "internships.add"),
    ("internships", r"^/api/internships/\d+/?$", "GET", "internships.view"),
    ("internships", r"^/api/internships/\d+/?$", "PUT", "internships.edit"),
    ("internships", r"^/api/internships/\d+/?$", "DELETE", "internships.delete"),
    ("internships", r"^/api/internships/\d+/status/?$", "POST", "internships.edit"),
    ("internships", r"^/api/internship-providers/?$", "GET", "internships.view"),
    ("internships", r"^/api/internship-providers/?$", "POST", "internships.add"),
    ("internships", r"^/api/internship-providers/\d+/?$", "GET", "internships.view"),
    ("internships", r"^/api/internship-providers/\d+/?$", "PUT", "internships.edit"),
    ("internships", r"^/api/internship-providers/\d+/?$", "DELETE", "internships.delete"),
    ("internships", r"^/api/internship-applications/?$", "GET", "internships.view"),
    ("internships", r"^/api/internship-applications/?$", "POST", "internships.add"),
    ("internships", r"^/api/internship-applications/\d+/?$", "GET", "internships.view"),
    ("internships", r"^/api/internship-applications/\d+/?$", "PUT", "internships.edit"),
    ("internships", r"^/api/internship-applications/\d+/?$", "DELETE", "internships.delete"),
    ("internships", r"^/api/internship-enquiry/\d+/convert/?$", "POST", "internships.edit"),

    # ==========================
    # 8. STAFF MANAGEMENT (Sensitive)
    # ==========================
    ("staff", r"^/admin-panel/users/staff/?$", "GET", "staff.view"),
    ("staff", r"^/api/admin/staff/add/?$", "POST", "staff.add"),
    ("staff", r"^/api/admin/staff/\d+/update/?$", "POST", "staff.edit"),
    ("staff", r"^/api/admin/staff/\d+/update/?$", "PUT", "staff.edit"),
    ("staff", r"^/api/admin/staff/\d+/delete/?$", "POST", "staff.delete"),
    ("staff", r"^/api/admin/staff/\d+/delete/?$", "DELETE", "staff.delete"),
    ("staff", r"^/api/admin/staff/\d+/detail/?$", "GET", "staff.view"),
    ("staff", r"^/api/admin/staff/\d+/record-payment/?$", "POST", "staff.view_salary"),
    ("staff", r"^/api/admin/staff/export/?$", "GET", "staff.export"),

    # ==========================
    # 9. ROLE & PERMISSIONS
    # ==========================
    ("roles", r"^/admin-panel/users/roles/?$", "GET", "roles.view"),
    ("roles", r"^/admin-panel/settings/roles/?$", "GET", "roles.view"),
    ("roles", r"^/admin-panel/users/permissions/?$", "GET", "roles.view"),
    ("roles", r"^/api/admin/roles/save/?$", "POST", "roles.add"),
    ("roles", r"^/api/admin/roles/\d+/?$", "GET", "roles.view"),
    ("roles", r"^/api/admin/roles/\d+/archive/?$", "POST", "roles.delete"),
    ("roles", r"^/api/admin/roles/\d+/duplicate/?$", "POST", "roles.add"),
    ("roles", r"^/api/admin/roles/export/?$", "GET", "roles.view"),

    # ==========================
    # 10. ADMIN USERS MANAGEMENT
    # ==========================
    ("admin_users", r"^/admin-panel/users/admin/?$", "GET", "admin_users.view"),
    ("admin_users", r"^/admin-panel/users/all/?$", "GET", "admin_users.view"),
    ("admin_users", r"^/admin-panel/users/add/?$", "GET", "admin_users.add"),
    ("admin_users", r"^/api/admin/users/?$", "GET", "admin_users.view"),
    ("admin_users", r"^/api/admin/users/?$", "POST", "admin_users.add"),
    ("admin_users", r"^/api/admin/users/\d+/?$", "GET", "admin_users.view"),
    ("admin_users", r"^/api/admin/users/\d+/?$", "PUT", "admin_users.edit"),
    ("admin_users", r"^/api/admin/users/\d+/?$", "POST", "admin_users.edit"),
    ("admin_users", r"^/api/admin/users/\d+/?$", "DELETE", "admin_users.delete"),

    # ==========================
    # 11. JOB POSTINGS
    # ==========================
    ("job_postings", r"^/admin-panel/companies/job-openings/?$", "GET", "job_postings.view"),
    ("job_postings", r"^/api/admin/jobs/?$", "GET", "job_postings.view"),
    ("job_postings", r"^/api/admin/jobs/?$", "POST", "job_postings.add"),
    ("job_postings", r"^/api/admin/jobs/save/?$", "POST", "job_postings.add"),
    ("job_postings", r"^/api/admin/jobs/\d+/?$", "GET", "job_postings.view"),
    ("job_postings", r"^/api/admin/jobs/\d+/?$", "PUT", "job_postings.edit"),
    ("job_postings", r"^/api/admin/jobs/\d+/status/?$", "POST", "job_postings.edit"),
    ("job_postings", r"^/api/admin/jobs/\d+/delete/?$", "POST", "job_postings.delete"),
    ("job_postings", r"^/api/admin/jobs/\d+/delete/?$", "DELETE", "job_postings.delete"),
    ("job_postings", r"^/api/company-requirements/?$", "GET", "job_postings.view"),
    ("job_postings", r"^/api/company-requirements/?$", "POST", "job_postings.add"),
    ("job_postings", r"^/api/company-requirement/\d+/?$", "GET", "job_postings.view"),
    ("job_postings", r"^/api/company-requirement/\d+/?$", "PUT", "job_postings.edit"),
    ("job_postings", r"^/api/company-requirement/\d+/?$", "DELETE", "job_postings.delete"),

    # ==========================
    # 12. JOB CATEGORIES
    # ==========================
    ("job_categories", r"^/admin-panel/job-categories/?$", "GET", "job_categories.view"),
    ("job_categories", r"^/api/admin/job-categories/save/?$", "POST", "job_categories.add"),
    ("job_categories", r"^/api/admin/job-categories/seed/?$", "POST", "job_categories.add"),
    ("job_categories", r"^/api/admin/job-categories/\d+/status/?$", "POST", "job_categories.edit"),
    ("job_categories", r"^/api/admin/job-categories/\d+/delete/?$", "POST", "job_categories.delete"),
    ("job_categories", r"^/api/admin/job-categories/\d+/delete/?$", "DELETE", "job_categories.delete"),

    # ==========================
    # 13. JOB APPROVALS
    # ==========================
    ("job_approvals", r"^/admin-panel/companies/requirements/active/?$", "GET", "job_approvals.view"),
    ("job_approvals", r"^/admin-panel/companies/job-approvals/?$", "GET", "job_approvals.view"),
    ("job_approvals", r"^/api/admin/job-approvals/?$", "GET", "job_approvals.view"),
    ("job_approvals", r"^/api/admin/job-approvals/\d+/approve/?$", "POST", "job_approvals.approve"),
    ("job_approvals", r"^/api/admin/job-approvals/\d+/reject/?$", "POST", "job_approvals.approve"),

    # ==========================
    # 14. JOB APPLICATIONS
    # ==========================
    ("applications", r"^/admin-panel/job-applications", "GET", "applications.view"),
    ("applications", r"^/api/admin/applications/\d+/approve/?$", "POST", "applications.approve"),
    ("applications", r"^/api/admin/applications/\d+/reject/?$", "POST", "applications.approve"),
    ("applications", r"^/api/admin/applications/\d+/assign-employer/?$", "POST", "applications.approve"),
    ("applications", r"^/api/admin/applications/\d+/override-step/?$", "POST", "applications.approve"),
    ("applications", r"^/api/admin/applications/bulk-approve/?$", "POST", "applications.approve"),

    # ==========================
    # 15. SHORTLISTED CANDIDATES
    # ==========================
    ("shortlisted", r"^/admin-panel/candidates/shortlisted/?$", "GET", "shortlisted.view"),

    # ==========================
    # 16. INTERVIEWS
    # ==========================
    ("interviews", r"^/admin-panel/candidates/interviews", "GET", "interviews.view"),
    ("interviews", r"^/api/interviews/?$", "GET", "interviews.view"),
    ("interviews", r"^/api/interviews/\d+/?$", "GET", "interviews.view"),
    ("interviews", r"^/api/interviews/\d+/?$", "DELETE", "interviews.delete"),
    ("interviews", r"^/api/admin/schedule-interview/?$", "POST", "interviews.add"),
    ("interviews", r"^/api/interviews/\d+/reschedule/?$", "POST", "interviews.edit"),
    ("interviews", r"^/api/interviews/\d+/complete/?$", "POST", "interviews.edit"),
    ("interviews", r"^/api/interviews/\d+/cancel/?$", "POST", "interviews.edit"),

    # ==========================
    # 17. CANDIDATE SELECTIONS
    # ==========================
    ("selections", r"^/admin-panel/candidates/selected/?$", "GET", "selections.view"),

    # ==========================
    # 18. OFFER LETTERS
    # ==========================
    ("offer_letters", r"^/admin-panel/job-offers", "GET", "offer_letters.view"),
    ("offer_letters", r"^/admin-panel/offers", "GET", "offer_letters.view"),
    ("offer_letters", r"^/api/job-offers/?$", "GET", "offer_letters.view"),
    ("offer_letters", r"^/api/job-offers/?$", "POST", "offer_letters.add"),
    ("offer_letters", r"^/api/job-offer/\d+/?$", "DELETE", "offer_letters.delete"),
    ("offer_letters", r"^/api/job-offers/\d+/?$", "DELETE", "offer_letters.delete"),
    ("offer_letters", r"^/api/admin/job-offers/create/?$", "POST", "offer_letters.add"),

    # ==========================
    # 19. JOININGS & PLACEMENTS
    # ==========================
    ("joinings", r"^/admin-panel/placements", "GET", "joinings.view"),
    ("joinings", r"^/api/placements/?$", "GET", "joinings.view"),
    ("joinings", r"^/api/placements/?$", "POST", "joinings.add"),
    ("joinings", r"^/api/placement/\d+/?$", "GET", "joinings.view"),
    ("joinings", r"^/api/placement/\d+/?$", "PUT", "joinings.edit"),
    ("joinings", r"^/api/placement/\d+/?$", "DELETE", "joinings.delete"),
    ("joinings", r"^/api/admin/placements/mark-joined/?$", "POST", "joinings.edit"),

    # ==========================
    # 20. LEDGER
    # ==========================
    ("ledger", r"^/admin-panel/ledger/?$", "GET", "ledger.view"),
    ("ledger", r"^/api/admin/ledger/?$", "GET", "ledger.view"),
    ("ledger", r"^/api/admin/ledger/\d+/?$", "GET", "ledger.view"),
    ("ledger", r"^/api/admin/ledger/\d+/salary/?$", "POST", "ledger.edit"),
    ("ledger", r"^/api/admin/ledger/\d+/waive/?$", "POST", "ledger.edit"),
    ("ledger", r"^/api/admin/ledger/\d+/payer/?$", "POST", "ledger.edit"),
    ("ledger", r"^/api/admin/ledger/sync/?$", "POST", "ledger.edit"),
    ("ledger", r"^/api/admin/ledger/export/?$", "GET", "ledger.export"),

    # ==========================
    # 21. INVOICES & DOCUMENTS
    # ==========================
    ("invoices", r"^/admin-panel/documents/joining/?$", "GET", "invoices.view"),
    ("invoices", r"^/admin-panel/documents", "GET", "invoices.view"),
    ("invoices", r"^/api/admin/documents/?$", "GET", "invoices.view"),

    # ==========================
    # 22. PAYMENTS
    # ==========================
    ("payments", r"^/admin-panel/ledger/payments/?$", "GET", "payments.view"),
    ("payments", r"^/api/admin/ledger/payments/?$", "GET", "payments.view"),
    ("payments", r"^/api/admin/ledger/\d+/payment/?$", "POST", "payments.add"),

    # ==========================
    # 23. COMMISSION MANAGEMENT
    # ==========================
    ("commission", r"^/admin-panel/placements/reports/?$", "GET", "commission.view"),

    # ==========================
    # 24. EMAIL COMPOSE
    # ==========================
    ("comm_compose", r"^/admin-panel/communication/compose/?$", "GET", "comm_compose.view"),
    ("comm_compose", r"^/admin-panel/communication/compose/?$", "POST", "comm_compose.add"),

    # ==========================
    # 25. EMAIL SENT HISTORY
    # ==========================
    ("comm_history", r"^/admin-panel/communication/history", "GET", "comm_history.view"),
    ("comm_history", r"^/api/admin/communication/bulk-status/?$", "GET", "comm_history.view"),
    ("comm_history", r"^/api/admin/communication/export-recipients/?$", "GET", "comm_history.export"),

    # ==========================
    # 26. MESSAGE TEMPLATES
    # ==========================
    ("comm_templates", r"^/admin-panel/communication/templates/?$", "GET", "comm_templates.view"),
    ("comm_templates", r"^/admin-panel/communication/templates/?$", "POST", "comm_templates.add"),
    ("comm_templates", r"^/api/admin/communication/template-json/?$", "GET", "comm_templates.view"),

    # ==========================
    # 27. DELIVERY SETTINGS
    # ==========================
    ("comm_settings", r"^/admin-panel/communication/settings/?$", "GET", "comm_settings.view"),
    ("comm_settings", r"^/admin-panel/communication/settings/?$", "POST", "comm_settings.edit"),

    # ==========================
    # 28. REPORTS
    # ==========================
    ("reports", r"^/admin-panel/reports", "GET", "reports.view"),

    # ==========================
    # 29. ACTIVITY & LOGIN LOGS
    # ==========================
    ("activity_log", r"^/admin-panel/logs", "GET", "activity_log.view"),
    ("activity_log", r"^/admin-panel/users/login-activity/?$", "GET", "activity_log.view"),

    # ==========================
    # 30. SYSTEM SETTINGS
    # ==========================
    ("system_settings", r"^/admin-panel/settings", "GET", "system_settings.view"),
    ("system_settings", r"^/admin-panel/settings", "POST", "system_settings.edit"),

    # ==========================
    # 31. WEBSITE MANAGEMENT
    # ==========================
    ("website_management", r"^/admin-panel/website", "GET", "website_management.view"),
    ("website_management", r"^/admin-panel/website", "POST", "website_management.edit"),
    ("website_management", r"^/api/admin/website", "POST", "website_management.edit"),
    ("website_management", r"^/admin-panel/api/admin/website/toggle-repeater-visible/?$", "POST", "website_management.edit"),
    ("website_management", r"^/admin-panel/website/services/api/toggle-repeater-visible/?$", "POST", "website_management.edit"),
    ("website_management", r"^/api/admin/upload-image/?$", "POST", "website_management.edit"),
]

def get_url_permission_map_grouped():
    """Group the complete URL permission map by module."""
    grouped = {}
    for mod_key, pattern, method, perm in URL_PERMISSION_MAP:
        if mod_key not in grouped:
            grouped[mod_key] = []
        grouped[mod_key].append({
            "pattern": pattern,
            "method": method,
            "permission": perm,
        })
    return grouped
