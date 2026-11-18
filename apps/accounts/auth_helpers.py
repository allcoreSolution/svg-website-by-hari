import os
import time
import uuid
from functools import wraps
from django.conf import settings
from django.http import JsonResponse
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from .models import AdminUser, CandidateAccount

signer = TimestampSigner()
RESET_MINUTES = 30
LOGIN_ATTEMPTS = {}

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')

def is_rate_limited(key, limit=5, window=900):
    now = time.time()
    attempts = [t for t in LOGIN_ATTEMPTS.get(key, []) if now - t < window]
    LOGIN_ATTEMPTS[key] = attempts
    return len(attempts) >= limit

def record_attempt(key):
    LOGIN_ATTEMPTS.setdefault(key, []).append(time.time())

def admin_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        admin_id = request.session.get('admin_id')
        if not admin_id:
            if request.path.startswith('/api/') or request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"status": "error", "message": "Please log in as admin."}, status=401)
            from django.shortcuts import redirect
            return redirect('/admin-panel/login/')
        
        admin = getattr(request, 'admin_user', None)
        if not admin:
            admin = AdminUser.objects.filter(id=admin_id, is_active=True).select_related('role').first()
            if not admin:
                request.session.flush()
                if request.path.startswith('/api/') or request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({"status": "error", "message": "Please log in as admin."}, status=401)
                from django.shortcuts import redirect
                return redirect('/admin-panel/login/')
            request.admin_user = admin
        return view_func(request, *args, **kwargs)
    return wrapped


def permission_required(perm_code):
    """
    Decorator for views requiring a specific permission code.
    Super Admins automatically pass.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            admin_id = request.session.get('admin_id')
            if not admin_id:
                if request.path.startswith('/api/') or request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({"status": "error", "message": "Please log in as admin."}, status=401)
                from django.shortcuts import redirect
                return redirect('/admin-panel/login/')

            admin = getattr(request, 'admin_user', None)
            if not admin:
                admin = AdminUser.objects.filter(id=admin_id, is_active=True).select_related('role').first()
                if not admin:
                    request.session.flush()
                    if request.path.startswith('/api/') or request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({"status": "error", "message": "Account inactive or invalid."}, status=401)
                    from django.shortcuts import redirect
                    return redirect('/admin-panel/login/')
                request.admin_user = admin

            if not admin.has_perm(perm_code):
                from apps.enquiries.models import log_activity
                log_activity("security", "Permission Denied", f"Admin {admin.email} denied {perm_code} on {request.path}")
                if request.path.startswith('/api/') or request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({"status": "error", "message": f"Permission denied. Required: {perm_code}"}, status=403)
                from django.shortcuts import render
                return render(request, 'dashboard/admin_403.html', {
                    "admin_user": admin,
                    "required_perm": perm_code,
                    "attempted_url": request.path
                }, status=403)

            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator

def candidate_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        candidate_id = request.session.get('candidate_id')
        if not candidate_id:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                return JsonResponse({"status": "error", "message": "Please log in to access this page."}, status=401)
            from django.shortcuts import redirect
            return redirect(f"/candidate/login/?next={request.path}")
        
        try:
            candidate = CandidateAccount.objects.get(id=candidate_id)
            if not candidate.is_approved or candidate.approval_status != 'approved':
                request.session.pop('candidate_id', None)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                    return JsonResponse({"status": "error", "message": "Your candidate account is not approved yet."}, status=403)
                from django.shortcuts import redirect
                return redirect("/candidate/login/")
            request.candidate_user = candidate
        except CandidateAccount.DoesNotExist:
            request.session.pop('candidate_id', None)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                return JsonResponse({"status": "error", "message": "Please log in as candidate."}, status=401)
            from django.shortcuts import redirect
            return redirect("/candidate/login/")

        return view_func(request, *args, **kwargs)
    return wrapped

def employer_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        employer_id = request.session.get('employer_id')
        if not employer_id:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                return JsonResponse({"status": "error", "message": "Please log in to access this page."}, status=401)
            from django.shortcuts import redirect
            return redirect(f"/employer/login/?next={request.path}")
        
        try:
            from .models import EmployerAccount
            employer = EmployerAccount.objects.get(id=employer_id)
            if employer.status != 'APPROVED':
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                    return JsonResponse({"status": "error", "message": f"Your employer account is currently {employer.status}."}, status=403)
                from django.shortcuts import redirect
                return redirect("/employer/pending/")
            request.employer_user = employer
        except Exception:
            request.session.pop('employer_id', None)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                return JsonResponse({"status": "error", "message": "Please log in as employer."}, status=401)
            from django.shortcuts import redirect
            return redirect("/employer/login/")

        return view_func(request, *args, **kwargs)
    return wrapped

def allowed_file(filename: str) -> bool:
    allowed_exts = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts

def save_resume_file(uploaded_file):
    if not uploaded_file:
        return None
    
    filename = uploaded_file.name
    if not allowed_file(filename):
        raise ValueError("Only PDF, DOC and DOCX files are allowed.")
    
    if uploaded_file.size > 10 * 1024 * 1024:
        raise ValueError("File size must not exceed 10 MB.")
    
    ext = filename.rsplit('.', 1)[1].lower()
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    
    upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads", "resumes")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, stored_name)
    file_bytes = b"".join(chunk for chunk in uploaded_file.chunks())
    with open(file_path, 'wb+') as destination:
        destination.write(file_bytes)

    try:
        from apps.candidates.models import UploadedFile
        ctype = getattr(uploaded_file, 'content_type', '') or 'application/pdf'
        UploadedFile.objects.update_or_create(
            name=stored_name,
            defaults={
                'file_data': file_bytes,
                'content_type': ctype,
                'file_size': len(file_bytes),
                'original_name': filename,
            }
        )
    except Exception:
        pass
            
    return stored_name

def save_employer_document_file(uploaded_file):
    if not uploaded_file:
        return None
    
    filename = uploaded_file.name
    if not allowed_file(filename):
        raise ValueError("Only PDF, DOC, DOCX, PNG, JPG files are allowed.")
    
    if uploaded_file.size > 10 * 1024 * 1024:
        raise ValueError("File size must not exceed 10 MB.")
    
    ext = filename.rsplit('.', 1)[1].lower()
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    
    upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads", "company_documents")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, stored_name)
    file_bytes = b"".join(chunk for chunk in uploaded_file.chunks())
    with open(file_path, 'wb+') as destination:
        destination.write(file_bytes)

    try:
        from apps.candidates.models import UploadedFile
        ctype = getattr(uploaded_file, 'content_type', '') or 'application/pdf'
        UploadedFile.objects.update_or_create(
            name=stored_name,
            defaults={
                'file_data': file_bytes,
                'content_type': ctype,
                'file_size': len(file_bytes),
                'original_name': filename,
            }
        )
    except Exception:
        pass
            
    return stored_name

def save_offer_letter_file(uploaded_file):
    if not uploaded_file:
        return None
    
    filename = uploaded_file.name
    if not allowed_file(filename):
        raise ValueError("Only PDF, DOC, DOCX, PNG, JPG files are allowed for Offer Letters.")
    
    if uploaded_file.size > 15 * 1024 * 1024:
        raise ValueError("File size must not exceed 15 MB.")
    
    ext = filename.rsplit('.', 1)[1].lower()
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    
    upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads", "offer_letters")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, stored_name)
    file_bytes = b"".join(chunk for chunk in uploaded_file.chunks())
    with open(file_path, 'wb+') as destination:
        destination.write(file_bytes)

    try:
        from apps.candidates.models import UploadedFile
        ctype = getattr(uploaded_file, 'content_type', '') or 'application/pdf'
        UploadedFile.objects.update_or_create(
            name=stored_name,
            defaults={
                'file_data': file_bytes,
                'content_type': ctype,
                'file_size': len(file_bytes),
                'original_name': filename,
            }
        )
    except Exception:
        pass
            
    return stored_name

def delete_resume_file(stored_filename):
    if not stored_filename:
        return
    file_path = os.path.join(settings.MEDIA_ROOT, "uploads", "resumes", stored_filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass
    try:
        from apps.candidates.models import UploadedFile
        UploadedFile.objects.filter(name=stored_filename).delete()
    except Exception:
        pass

