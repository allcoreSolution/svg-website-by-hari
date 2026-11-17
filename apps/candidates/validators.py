import re
from datetime import datetime, date
from django.utils import timezone

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PHONE_REGEX = re.compile(r'^\+?[0-9\s\-]{10,20}$')

VALID_CANDIDATE_STATUSES = [
    'New', 'Application Received', 'Under Review', 'Pending', 'Shortlisted', 'Interview Scheduled', 'Interview',
    'Scheduled', 'Selected', 'Joined', 'Rejected', 'Placed', 'Completed', 'Cancelled'
]

VALID_INTERVIEW_STATUSES = ['Scheduled', 'Rescheduled', 'Completed', 'Cancelled']
VALID_INTERVIEW_RESULTS = ['Selected', 'Rejected', 'On Hold', 'Under Review', '']

def validate_candidate_data(data):
    """
    Validates candidate registration/update inputs.
    Returns (is_valid, error_dict)
    """
    errors = {}
    
    full_name = str(data.get('full_name') or data.get('name') or '').strip()
    email = str(data.get('email') or '').strip()
    phone = str(data.get('phone') or data.get('mobile') or '').strip()

    if not full_name:
        errors['full_name'] = "Full name is required."
    elif len(full_name) < 2:
        errors['full_name'] = "Full name must be at least 2 characters."

    if not email:
        errors['email'] = "Email address is required."
    elif not EMAIL_REGEX.match(email):
        errors['email'] = "Invalid email format."

    if not phone:
        errors['phone'] = "Phone number is required."
    elif not PHONE_REGEX.match(phone):
        errors['phone'] = "Phone number must be at least 10 digits."

    exp_raw = data.get('experience')
    if exp_raw is not None and str(exp_raw).strip() != '':
        try:
            exp_val = int(exp_raw)
            if exp_val < 0 or exp_val > 60:
                errors['experience'] = "Experience must be between 0 and 60 years."
        except (ValueError, TypeError):
            errors['experience'] = "Experience must be a valid integer."

    status = data.get('status')
    if status and status not in VALID_CANDIDATE_STATUSES:
        errors['status'] = f"Invalid status '{status}'."

    if errors:
        first_err = list(errors.values())[0]
        return False, {
            "status": "error",
            "message": first_err,
            "errors": errors
        }
    return True, None

def validate_interview_data(data, current_interview_id=None):
    """
    Validates interview schedule or reschedule inputs.
    Returns (is_valid, error_dict, parsed_date, parsed_time)
    """
    errors = {}
    
    date_str = str(data.get('interview_date') or '').strip()
    time_str = str(data.get('interview_time') or '').strip()
    
    parsed_d = None
    parsed_t = None

    if not date_str:
        errors['interview_date'] = "Interview date is required."
    else:
        try:
            parsed_d = datetime.strptime(date_str, "%Y-%m-%d").date()
            today = timezone.now().date()
            if parsed_d < today:
                errors['interview_date'] = f"Interview date cannot be in the past ({date_str}). Please select today or a future date."
        except ValueError:
            errors['interview_date'] = "Invalid date format. Use YYYY-MM-DD."

    if not time_str:
        errors['interview_time'] = "Interview time is required."
    else:
        for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M%p"):
            try:
                parsed_t = datetime.strptime(time_str, fmt).time()
                break
            except ValueError:
                pass
        if not parsed_t:
            errors['interview_time'] = "Invalid time format. Use HH:MM."

    # Check slot duplication if both date and time are valid
    if parsed_d and parsed_t and not errors:
        from apps.candidates.models import Interview
        qs = Interview.objects.filter(
            interview_date=parsed_d,
            interview_time=parsed_t,
            status__in=['Scheduled', 'Rescheduled']
        )
        if current_interview_id:
            qs = qs.exclude(id=current_interview_id)

        if qs.exists():
            existing = qs.first()
            errors['interview_time'] = f"Time slot {parsed_t.strftime('%H:%M')} on {parsed_d.strftime('%Y-%m-%d')} is already booked for candidate '{existing.candidate_name}'."

    if errors:
        first_err = list(errors.values())[0]
        return False, {
            "status": "error",
            "message": first_err,
            "errors": errors
        }, None, None

    return True, None, parsed_d, parsed_t
