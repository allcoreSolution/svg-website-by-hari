"""
Central status constants and mapping for Candidates and Application Progress Tracking.
"""

# New Status Constants (matching the 7-step flow)
STATUS_CANDIDATE_APPLIES = "Candidate Applies Job"
STATUS_APPLICATION_SUBMITTED = "Application Submitted"
STATUS_APPLICATION_RECEIVED = "Application Received"
STATUS_EMPLOYER_REVIEWS = "Employer Reviews"
STATUS_UNDER_REVIEW = "Under Review"
STATUS_SHORTLISTED = "Shortlisted"
STATUS_INTERVIEW_SCHEDULED = "Interview Scheduled"
STATUS_INTERVIEW = "Interview"
STATUS_OFFER_RELEASED = "Offer Released"
STATUS_SELECTED = "Selected"
STATUS_JOINED = "Joined"
STATUS_REJECTED = "Rejected"
STATUS_CANCELLED = "Cancelled"

# Audience resolution status lists
SHORTLISTED_STATUSES = ["Shortlisted"]
SELECTED_STATUSES = ["Selected", "Offer Released", "Offer Sent", "Offered", "Accepted", "Joined", "Candidate Joined", "Placed"]

# Master definition of the 7-step Application Flow
APPLICATION_FLOW_STEPS = [
    {"step": 1, "key": "applied", "label": "Candidate Applies Job", "icon": "ti-user-check", "color": "blue"},
    {"step": 2, "key": "submitted", "label": "Application Submitted", "icon": "ti-send", "color": "blue"},
    {"step": 3, "key": "employer_reviews", "label": "Employer Reviews", "icon": "ti-eye", "color": "blue"},
    {"step": 4, "key": "shortlisted", "label": "Shortlisted", "icon": "ti-star", "color": "green"},
    {"step": 5, "key": "interview", "label": "Interview Scheduled", "icon": "ti-calendar-event", "color": "orange"},
    {"step": 6, "key": "offer", "label": "Offer Released", "icon": "ti-file-certificate", "color": "orange"},
    {"step": 7, "key": "joined", "label": "Candidate Joined", "icon": "ti-award", "color": "orange"},
]

# Legacy step list for backwards compatibility
CANDIDATE_PROGRESS_STEPS = APPLICATION_FLOW_STEPS

# Map DB status strings to step index (1..7)
STATUS_STEP_MAP = {
    "Candidate Applies Job": 1,
    "Application Submitted": 2,
    "Application Received": 2,
    "New": 2,
    "Employer Reviews": 3,
    "Pending": 3,
    "Under Review": 3,
    "Shortlisted": 4,
    "Interview Scheduled": 5,
    "Interview": 5,
    "Scheduled": 5,
    "Offer Released": 6,
    "Selected": 6,
    "Offer Sent": 6,
    "Joined": 7,
    "Candidate Joined": 7,
    "Placed": 7,
    "Completed": 7,
    "Rejected": 0,
    "Cancelled": 0,
}

STATUS_BADGE_MAP = {
    "Candidate Applies Job": "bg-secondary text-white",
    "Application Submitted": "bg-warning text-dark",
    "Application Received": "bg-warning text-dark",
    "New": "bg-warning text-dark",
    "Employer Reviews": "bg-info text-dark",
    "Pending": "bg-info text-dark",
    "Under Review": "bg-info text-dark",
    "Shortlisted": "bg-primary text-white",
    "Interview Scheduled": "bg-purple text-white",
    "Interview": "bg-purple text-white",
    "Scheduled": "bg-purple text-white",
    "Offer Released": "bg-warning text-dark",
    "Selected": "bg-warning text-dark",
    "Offer Sent": "bg-warning text-dark",
    "Joined": "bg-success text-white",
    "Candidate Joined": "bg-success text-white",
    "Placed": "bg-success text-white",
    "Completed": "bg-success text-white",
    "Rejected": "bg-danger text-white",
    "Cancelled": "bg-secondary text-white",
}

ALLOWED_TRANSITIONS = {
    "Application Submitted": {"Employer Reviews", "Shortlisted", "Rejected"},
    "Employer Reviews": {"Shortlisted", "Rejected"},
    "Shortlisted": {"Interview Scheduled", "Interview", "Selected", "Rejected"},
    "Interview Scheduled": {"Interview", "Selected", "Offer Released", "Rejected", "Cancelled"},
    "Interview": {"Selected", "Offer Released", "Rejected", "Cancelled"},
    "Offer Released": {"Joined", "Placed", "Rejected", "Cancelled"},
    "Offer Sent": {"Accepted", "Joined", "Placed", "Rejected", "Cancelled"},
    "New": {"Employer Reviews", "Shortlisted", "Rejected"},
    "Application Received": {"Employer Reviews", "Shortlisted", "Rejected"},
    "Under Review": {"Shortlisted", "Rejected"},
    "Scheduled": {"Interview", "Selected", "Offer Released", "Rejected", "Cancelled"},
    "Selected": {"Offer Released", "Offer Sent", "Joined", "Placed", "Rejected", "Cancelled"},
}

def get_candidate_step(status_str):
    return STATUS_STEP_MAP.get(status_str, 2)

def get_badge_class(status_str):
    return STATUS_BADGE_MAP.get(status_str, "bg-secondary text-white")

