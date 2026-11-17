SPAM_PHRASES = [
    "crypto", "bitcoin", "casino", "viagra", "seo service", "backlink",
    "loan offer", "investment opportunity", "telegram:", "whatsapp:"
]

BUSINESS_SERVICES = [
    "Recruitment", "HR Consultancy", "Payroll Outsourcing",
    "Contract Staffing", "Manpower Supply", "Skilled Manpower",
    "Unskilled Manpower", "Industrial Workforce", "Factory Staff", "Office Staff"
]

CANDIDATE_SERVICES = [
    "Job Application", "Candidate Enquiry", "Career Opportunity",
    "Resume Submission", "Job Seeking"
]

CANDIDATE_KEYWORDS = [
    "job", "placement", "resume", "cv", "career",
    "vacancy", "interview", "apply", "salary"
]

CONTACT_STATUS_CHOICES = ["New", "Pending", "Contacted", "Under Review", "In Progress", "Resolved", "Closed", "Spam"]
COMPANY_STATUS_CHOICES = ["New", "Contacted", "Under Review", "Approved", "Rejected", "Spam"]
INTERNSHIP_STATUS_CHOICES = ["New", "Contacted", "Under Review", "Converted", "Rejected", "Spam"]

OPEN_STATUSES = {"new", "pending", "unread"}
IN_PROGRESS_STATUSES = {"contacted", "under review", "in progress", "interview", "shortlisted"}
RESOLVED_STATUSES = {"resolved", "approved", "completed", "converted", "selected", "active", "fulfilled", "placed"}
CLOSED_STATUSES = {"closed", "rejected", "cancelled", "expired", "spam"}

def bucket_of(model_type, status):
    st = str(status or "").strip().lower()
    if st in OPEN_STATUSES:
        return 'open'
    elif st in IN_PROGRESS_STATUSES:
        return 'in_progress'
    elif st in RESOLVED_STATUSES:
        return 'resolved'
    elif st in CLOSED_STATUSES:
        return 'closed'
    return 'open'

def classify_enquiry_type(service, message=""):
    svc_str = str(service or "").strip()
    msg_str = str(message or "").strip()

    if svc_str in BUSINESS_SERVICES:
        return "General"
    if svc_str in CANDIDATE_SERVICES:
        return "Candidate"
    if svc_str.lower() == "internship":
        return "General"

    combined = f"{svc_str} {msg_str}".lower()
    for kw in CANDIDATE_KEYWORDS:
        if kw in combined:
            return "Candidate"

    return "General"
