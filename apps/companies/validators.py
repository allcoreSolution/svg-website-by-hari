import re
from datetime import datetime

INDIAN_PHONE_REGEX = re.compile(r'^\+?[0-9\s\-\(\)]{8,20}$')
GSTIN_REGEX = re.compile(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', re.IGNORECASE)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

COMPANY_STATUSES = ["Active", "Inactive", "Blocked"]
REQUIREMENT_STATUSES = ["Active", "Closed", "Expired", "Draft"]
ENQUIRY_STATUSES = ["New", "Contacted", "Approved", "Rejected"]

def validate_email(email_str):
    if not email_str:
        return False, "Email address is required."
    email_str = email_str.strip()
    if not EMAIL_REGEX.match(email_str):
        return False, "Invalid email address format."
    return True, ""

def validate_phone(phone_str):
    if not phone_str:
        return False, "Phone number is required."
    phone_str = phone_str.strip()
    if not INDIAN_PHONE_REGEX.match(phone_str):
        return False, "Invalid phone number format. Provide an 8-15 digit phone number."
    return True, ""

def validate_website(url_str):
    if not url_str:
        return True, ""  # Website is optional
    url_str = url_str.strip()
    if not url_str.startswith("http://") and not url_str.startswith("https://"):
        url_str = "https://" + url_str
    if not URL_REGEX.match(url_str):
        return False, "Invalid website URL."
    return True, ""

def validate_gstin(gst_str):
    if not gst_str:
        return True, ""  # GST is optional
    gst_str = gst_str.strip().upper()
    if len(gst_str) != 15 or not GSTIN_REGEX.match(gst_str):
        return False, "Invalid GSTIN number. GSTIN must be 15 alphanumeric characters matching standard GST format."
    return True, ""

def validate_vacancies(vacancies_val):
    try:
        val = int(vacancies_val)
        if val < 1 or val > 1000:
            return False, "Vacancies must be between 1 and 1000."
    except (ValueError, TypeError):
        return False, "Vacancies must be a valid integer."
    return True, ""

def validate_deadline(deadline_str):
    if not deadline_str:
        return True, ""
    deadline_str = deadline_str.strip()
    # If YYYY-MM-DD format, ensure it's not in the past
    if re.match(r'^\d{4}-\d{2}-\d{2}$', deadline_str):
        try:
            dt = datetime.strptime(deadline_str, "%Y-%m-%d").date()
            if dt < datetime.now().date():
                return False, "Application deadline cannot be in the past."
        except ValueError:
            return False, "Invalid date format for deadline."
    return True, ""
