import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import AdminUser, Role, AdminLoginLog
from .auth_helpers import admin_required, permission_required, get_client_ip, is_rate_limited, record_attempt
from apps.enquiries.models import log_activity

signer = TimestampSigner()
RESET_MINUTES = 30

@require_http_methods(["POST"])
def admin_login(request):
    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    
    ip = get_client_ip(request)
    key = f"login:{ip}"
    
    if is_rate_limited(key, limit=5, window=900):
        return JsonResponse({"status": "error", "message": "Too many attempts. Try again in 15 minutes."}, status=429)
    
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    try:
        admin = AdminUser.objects.select_related('role').get(email=email, is_active=True)
        if admin.verify_password(password):
            request.session.flush()
            request.session['admin_id'] = admin.id
            request.session['admin_email'] = admin.email
            request.session.set_expiry(8 * 3600)  # 8 hours
            admin.last_login_at = timezone.now()
            admin.last_login_ip = ip
            admin.save(update_fields=['last_login_at', 'last_login_ip'])
            AdminLoginLog.objects.create(email=email, ip_address=ip, status='success', user_agent=user_agent)
            log_activity("admin", "Admin Login", f"Admin {email} logged in successfully")
            return JsonResponse({"status": "success", "message": "Login successful.", "user": admin.to_dict()})
        else:
            record_attempt(key)
            AdminLoginLog.objects.create(email=email, ip_address=ip, status='failed', user_agent=user_agent)
            return JsonResponse({"status": "error", "message": "Wrong email or password."}, status=401)
    except AdminUser.DoesNotExist:
        record_attempt(key)
        AdminLoginLog.objects.create(email=email, ip_address=ip, status='failed', user_agent=user_agent)
        return JsonResponse({"status": "error", "message": "Wrong email or password."}, status=401)

@require_http_methods(["POST"])
def admin_logout(request):
    admin_email = request.session.get('admin_email', '')
    request.session.flush()
    if admin_email:
        log_activity("admin", "Admin Logout", f"Admin {admin_email} logged out")
    return JsonResponse({"status": "success", "message": "Logged out successfully."})

@require_http_methods(["GET"])
@admin_required
def admin_me(request):
    admin_id = request.session.get('admin_id')
    try:
        admin = AdminUser.objects.get(id=admin_id)
        return JsonResponse({"id": admin.id, "email": admin.email})
    except AdminUser.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User not found."}, status=404)

@require_http_methods(["POST"])
def admin_forgot_password(request):
    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    email = (data.get("email") or "").strip().lower()
    ip = get_client_ip(request)
    key = f"forgot:{ip}"
    
    if is_rate_limited(key, limit=5, window=900):
        return JsonResponse({"status": "error", "message": "Too many requests. Try again in 15 minutes."}, status=429)
    record_attempt(key)

    try:
        admin = AdminUser.objects.get(email=email, is_active=True)
        # Generate token with signature
        token_payload = f"{admin.id}:{admin.password_hash[-12:]}"
        token = signer.sign(token_payload)
        reset_link = f"{settings.SITE_URL}/admin-panel/login/?token={token}"
        
        try:
            send_mail(
                subject="Sky Vision Admin - Reset Your Password",
                message=f"Open this link to set a new password (valid for {RESET_MINUTES} minutes):\n\n{reset_link}\n\nIf you did not request this, ignore this email.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin.email],
                fail_silently=True
            )
        except Exception as e:
            print("[Email note]:", e)
        print(f"\n[PASSWORD RESET LINK for {email}]:\n{reset_link}\n")
    except AdminUser.DoesNotExist:
        pass

    return JsonResponse({
        "status": "success",
        "message": "If that email is registered, a reset link has been sent."
    })

@require_http_methods(["POST"])
def admin_reset_password(request):
    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    token = data.get("token") or ""
    password = data.get("password") or ""
    
    if len(password) < 8:
        return JsonResponse({"status": "error", "message": "Password must be at least 8 characters."}, status=400)
    
    try:
        original_payload = signer.unsign(token, max_age=RESET_MINUTES * 60)
        admin_id_str, pass_tail = original_payload.split(":", 1)
        admin = AdminUser.objects.get(id=int(admin_id_str), is_active=True)
        
        if admin.password_hash[-12:] != pass_tail:
            return JsonResponse({"status": "error", "message": "This reset link has already been used. Request a new one."}, status=400)
            
        admin.set_password(password)
        admin.save(update_fields=['password_hash'])
        log_activity("admin", "Password Reset", f"Password changed for admin {admin.email}")
        return JsonResponse({"status": "success", "message": "Password changed successfully. You can log in now."})
    except (BadSignature, SignatureExpired):
        return JsonResponse({"status": "error", "message": "This reset link is invalid or has expired. Request a new one."}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": "Password reset failed."}, status=400)

@require_http_methods(["GET", "POST"])
@permission_required("admin_users.view")
def admin_users_api(request):
    if request.method == "GET":
        users = AdminUser.objects.select_related('role').all().order_by('-id')
        return JsonResponse([u.to_dict() for u in users], safe=False)
    
    # POST - Create new admin user (requires admin_users.add)
    if not request.admin_user.has_perm("admin_users.add"):
        return JsonResponse({"status": "error", "message": "Permission denied: admin_users.add required."}, status=403)

    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()
    phone = (data.get("phone") or "").strip()
    role_id = data.get("role_id")

    if not email or "@" not in email:
        return JsonResponse({"status": "error", "message": "Valid email address is required."}, status=400)
    if len(password) < 8:
        return JsonResponse({"status": "error", "message": "Password must be at least 8 characters."}, status=400)

    if AdminUser.objects.filter(email=email).exists():
        return JsonResponse({"status": "error", "message": "An admin with this email already exists."}, status=400)

    role = None
    if role_id:
        try:
            role = Role.objects.get(id=role_id, is_active=True)
        except Role.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Selected role does not exist."}, status=400)
    else:
        # Default to Viewer or Admin if not specified
        role = Role.objects.filter(name="Viewer").first() or Role.objects.first()

    # Only Super Admin can create another Super Admin
    if role and role.is_super and not request.admin_user.role.is_super:
        return JsonResponse({"status": "error", "message": "Only Super Admins can assign the Super Admin role."}, status=403)

    admin = AdminUser(
        email=email,
        full_name=full_name,
        phone=phone,
        role=role,
        created_by=request.admin_user
    )
    admin.set_password(password)
    admin.save()

    log_activity("security", "Admin User Created", f"New admin user {email} created with role {role.name if role else 'None'}")
    return JsonResponse({"status": "success", "message": "Admin user created successfully.", "user": admin.to_dict()})


@require_http_methods(["POST", "DELETE"])
@permission_required("admin_users.edit")
def admin_user_detail_api(request, id):
    try:
        admin = AdminUser.objects.select_related('role').get(id=id)
    except AdminUser.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Admin user not found."}, status=404)

    current_admin = request.admin_user

    # DELETE operation
    if request.method == "DELETE":
        if not current_admin.has_perm("admin_users.delete"):
            return JsonResponse({"status": "error", "message": "Permission denied: admin_users.delete required."}, status=403)

        if admin.id == current_admin.id:
            return JsonResponse({"status": "error", "message": "You cannot delete your own account."}, status=400)

        # Check if deleting the last active Super Admin
        if admin.role and admin.role.is_super:
            active_supers = AdminUser.objects.filter(role__is_super=True, is_active=True).count()
            if active_supers <= 1:
                return JsonResponse({"status": "error", "message": "Cannot delete the last active Super Admin."}, status=400)

        email = admin.email
        admin.delete()
        log_activity("security", "Admin User Deleted", f"Admin user {email} deleted by {current_admin.email}")
        return JsonResponse({"status": "success", "message": f"Admin user '{email}' deleted successfully."})

    # POST - Edit, Change Role, Reset Password, or Toggle Active Status
    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    action = data.get("action")

    # Action 1: Toggle active status
    if action == "toggle_status":
        if admin.id == current_admin.id:
            return JsonResponse({"status": "error", "message": "You cannot deactivate your own account."}, status=400)

        if admin.role and admin.role.is_super and admin.is_active:
            active_supers = AdminUser.objects.filter(role__is_super=True, is_active=True).count()
            if active_supers <= 1:
                return JsonResponse({"status": "error", "message": "Cannot deactivate the last active Super Admin."}, status=400)

        admin.is_active = not admin.is_active
        admin.save(update_fields=['is_active'])
        status_label = "activated" if admin.is_active else "deactivated"
        log_activity("security", "Admin Status Changed", f"Admin {admin.email} {status_label} by {current_admin.email}")
        return JsonResponse({"status": "success", "message": f"Admin {admin.email} has been {status_label}.", "is_active": admin.is_active})

    # Action 2: Change Role
    elif action == "change_role":
        if admin.id == current_admin.id:
            return JsonResponse({"status": "error", "message": "You cannot change your own role."}, status=400)

        new_role_id = data.get("role_id")
        try:
            new_role = Role.objects.get(id=new_role_id, is_active=True)
        except Role.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Target role not found."}, status=404)

        # Protect last active Super Admin from demotion
        if admin.role and admin.role.is_super and not new_role.is_super:
            active_supers = AdminUser.objects.filter(role__is_super=True, is_active=True).count()
            if active_supers <= 1:
                return JsonResponse({"status": "error", "message": "Cannot demote the last active Super Admin."}, status=400)

        old_role_name = admin.role.name if admin.role else "None"
        admin.role = new_role
        admin.save(update_fields=['role'])
        log_activity("security", "Admin Role Changed", f"Admin {admin.email} role changed from {old_role_name} to {new_role.name} by {current_admin.email}")
        return JsonResponse({"status": "success", "message": f"Role updated to '{new_role.name}'.", "user": admin.to_dict()})

    # Action 3: Reset Password
    elif action == "reset_password":
        new_password = data.get("password") or ""
        if len(new_password) < 8:
            return JsonResponse({"status": "error", "message": "Password must be at least 8 characters."}, status=400)

        admin.set_password(new_password)
        admin.save(update_fields=['password_hash'])
        log_activity("security", "Admin Password Reset", f"Password for admin {admin.email} reset by {current_admin.email}")
        return JsonResponse({"status": "success", "message": f"Password for {admin.email} updated successfully."})

    # Action 4: Update Profile Information
    else:
        fn = (data.get("full_name") or "").strip()
        ph = (data.get("phone") or "").strip()
        if fn:
            admin.full_name = fn
        admin.phone = ph
        admin.save(update_fields=['full_name', 'phone'])
        return JsonResponse({"status": "success", "message": "Profile updated successfully.", "user": admin.to_dict()})
