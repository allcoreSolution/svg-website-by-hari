import re
from .constants import SPAM_PHRASES

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PHONE_REGEX = re.compile(r'^\+?[0-9\s\-]{10,15}$')

def validate_name(name):
    n = str(name or "").strip()
    if not n or len(n) < 2 or len(n) > 100:
        return False, "Name must be between 2 and 100 characters."
    return True, n

def validate_email(email):
    e = str(email or "").strip().lower()
    if not e or len(e) > 120 or not EMAIL_REGEX.match(e):
        return False, "Please enter a valid email address."
    return True, e

def validate_phone(phone):
    p = str(phone or "").strip()
    # Remove spacing and dashes for validation
    digits_only = re.sub(r'[\s\-]', '', p)
    if not digits_only or len(digits_only) < 10 or len(digits_only) > 15 or not PHONE_REGEX.match(p):
        return False, "Please enter a valid phone number (at least 10 digits)."
    return True, p

def validate_service(service):
    s = str(service or "").strip()
    if not s:
        s = "General Inquiry"
    if len(s) > 100:
        s = s[:100]
    return True, s

def validate_message(message):
    m = str(message or "").strip()
    if len(m) > 2000:
        return False, "Message must not exceed 2000 characters."
    return True, m

def check_spam_phrases(text):
    t = str(text or "").lower()
    for phrase in SPAM_PHRASES:
        if phrase in t:
            return True
    return False
