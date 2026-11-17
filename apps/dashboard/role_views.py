import os
import csv
import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone

from apps.accounts.models import AdminUser, Role, RolePermission, AdminLoginLog
from apps.accounts.auth_helpers import admin_required, permission_required
from apps.accounts.permissions import MODULES, ACTION_LABELS, get_modules_by_section, get_all_permission_codes
from apps.enquiries.models import log_activity


# =========================================================================
# 1. ROLE LIST & MANAGEMENT VIEW (/admin-panel/users/roles/)
# =========================================================================

@admin_required
@permission_required("roles.view")
def admin_roles_list_view(request):
    """
    Dedicated User Roles Management Hub matching SVG Consultancy design system.
    Displays dynamic KPI stats, search, status filter, sorting, and roles table.
    """
    admin_user = request.admin_user

    # Filters
    search_q = (request.GET.get('q') or '').strip()
    status_filter = (request.GET.get('status') or '').strip()
    sort_by = (request.GET.get('sort') or 'newest').strip()
    page_num = request.GET.get('page', 1)

    all_roles = Role.objects.annotate(
        user_count=Count('users', filter=Q(users__is_active=True)),
        perm_count=Count('permissions', distinct=True)
    )

    # KPI Statistics
    total_roles = all_roles.count()
    active_roles = all_roles.filter(is_active=True).count()
    archived_roles = all_roles.filter(is_active=False).count()
    users_with_roles = AdminUser.objects.filter(role__isnull=False, is_active=True).count()
    pending_users = AdminUser.objects.filter(Q(role__isnull=True) | Q(role__is_active=False), is_active=True).count()

    # Apply Filters
    qs = all_roles
    if status_filter == 'active':
        qs = qs.filter(is_active=True)
    elif status_filter == 'archived':
        qs = qs.filter(is_active=False)

    if search_q:
        qs = qs.filter(
            Q(name__icontains=search_q) |
            Q(description__icontains=search_q)
        )

    # Sorting
    if sort_by == 'name':
        qs = qs.order_by('name')
    elif sort_by == 'users':
        qs = qs.order_by('-user_count', 'name')
    elif sort_by == 'oldest':
        qs = qs.order_by('id')
    else:  # newest
        qs = qs.order_by('-id')

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(page_num)

    # Section-grouped modules for the Permission Matrix modal
    modules_by_section = get_modules_by_section()
    all_perm_codes = get_all_permission_codes()

    context = {
        'admin_user': admin_user,
        'active_menu': 'roles',
        'sub_active': 'roles',
        'page_obj': page_obj,
        'roles_list': page_obj.object_list,
        'search_q': search_q,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'kpi': {
            'total_roles': total_roles,
            'active_roles': active_roles,
            'archived_roles': archived_roles,
            'users_with_roles': users_with_roles,
            'pending_users': pending_users,
        },
        'modules_by_section': modules_by_section,
        'all_perm_codes_json': json.dumps(all_perm_codes),
        'total_permissions_count': len(all_perm_codes),
    }

    return render(request, 'dashboard/roles_management.html', context)


# =========================================================================
# 2. PERMISSIONS OVERVIEW MATRIX (/admin-panel/users/permissions/)
# =========================================================================

@admin_required
@permission_required("roles.view")
def admin_permissions_matrix_view(request):
    """
    Overview Matrix displaying all roles against permissions grouped by section.
    """
    admin_user = request.admin_user
    roles = Role.objects.filter(is_active=True).order_by('-is_super', 'name')
    modules_by_section = get_modules_by_section()

    # Pre-build role permissions set map {role_id: set(perm_codes)}
    role_perm_map = {}
    for r in roles:
        if r.is_super:
            role_perm_map[r.id] = set(get_all_permission_codes())
        else:
            role_perm_map[r.id] = set(r.permissions.values_list('code', flat=True))

    matrix_sections = []
    for section_name, mods in modules_by_section.items():
        mod_rows = []
        for mod in mods:
            actions_data = []
            for act in mod['actions']:
                code = f"{mod['key']}.{act}"
                role_access = {r.id: (code in role_perm_map.get(r.id, set())) for r in roles}
                actions_data.append({
                    'code': code,
                    'action': act,
                    'label': ACTION_LABELS.get(act, act.title()),
                    'role_access': role_access,
                })
            mod_rows.append({
                'key': mod['key'],
                'label': mod['label'],
                'actions': actions_data,
            })
        matrix_sections.append({
            'section': section_name,
            'modules': mod_rows,
        })

    context = {
        'admin_user': admin_user,
        'active_menu': 'roles',
        'sub_active': 'permissions',
        'roles': roles,
        'matrix_sections': matrix_sections,
    }
    return render(request, 'dashboard/permissions_matrix.html', context)


# =========================================================================
# 3. ADMIN USERS MANAGEMENT VIEW (/admin-panel/users/admin/)
# =========================================================================

@admin_required
@permission_required("admin_users.view")
def admin_users_list_view(request):
    """
    Admin Users Directory with Add User modal, Role change, Password reset, and Deactivation.
    """
    admin_user = request.admin_user

    search_q = (request.GET.get('q') or '').strip()
    role_filter = (request.GET.get('role') or '').strip()
    status_filter = (request.GET.get('status') or '').strip()
    page_num = request.GET.get('page', 1)

    all_users = AdminUser.objects.select_related('role').all().order_by('-id')

    total_admins = all_users.count()
    active_admins = all_users.filter(is_active=True).count()
    inactive_admins = all_users.filter(is_active=False).count()
    roles_in_use = Role.objects.filter(users__isnull=False).distinct().count()

    qs = all_users
    if status_filter == 'active':
        qs = qs.filter(is_active=True)
    elif status_filter == 'inactive':
        qs = qs.filter(is_active=False)

    if role_filter:
        qs = qs.filter(role__id=role_filter)

    if search_q:
        qs = qs.filter(
            Q(email__icontains=search_q) |
            Q(full_name__icontains=search_q) |
            Q(phone__icontains=search_q)
        )

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(page_num)

    available_roles = Role.objects.filter(is_active=True).order_by('-is_super', 'name')

    context = {
        'admin_user': admin_user,
        'active_menu': 'staff',
        'sub_active': 'admin_users',
        'page_obj': page_obj,
        'users_list': page_obj.object_list,
        'available_roles': available_roles,
        'search_q': search_q,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'kpi': {
            'total_admins': total_admins,
            'active_admins': active_admins,
            'inactive_admins': inactive_admins,
            'roles_in_use': roles_in_use,
        }
    }
    return render(request, 'dashboard/admin_users_management.html', context)


# =========================================================================
# 4. LOGIN ACTIVITY LOGS VIEW (/admin-panel/users/login-activity/)
# =========================================================================

@admin_required
@permission_required("activity_log.view")
def admin_login_activity_view(request):
    """
    Login Activity records for admin users with status, IP, and timestamp.
    """
    admin_user = request.admin_user

    search_q = (request.GET.get('q') or '').strip()
    status_filter = (request.GET.get('status') or '').strip()
    page_num = request.GET.get('page', 1)

    qs = AdminLoginLog.objects.all().order_by('-created_at')

    total_logins = qs.count()
    success_logins = qs.filter(status='success').count()
    failed_logins = qs.filter(status='failed').count()

    if status_filter in ['success', 'failed']:
        qs = qs.filter(status=status_filter)

    if search_q:
        qs = qs.filter(
            Q(email__icontains=search_q) |
            Q(ip_address__icontains=search_q)
        )

    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(page_num)

    context = {
        'admin_user': admin_user,
        'active_menu': 'roles',
        'sub_active': 'login_activity',
        'page_obj': page_obj,
        'logs_list': page_obj.object_list,
        'search_q': search_q,
        'status_filter': status_filter,
        'kpi': {
            'total_logins': total_logins,
            'success_logins': success_logins,
            'failed_logins': failed_logins,
        }
    }
    return render(request, 'dashboard/admin_login_activity.html', context)


# =========================================================================
# 5. ROLE CRUD APIS (JSON)
# =========================================================================

@admin_required
@permission_required("roles.view")
def api_admin_role_detail(request, role_id):
    """Fetch details and assigned permissions of a role."""
    try:
        role = get_object_or_404(Role, id=role_id)
        if role.is_super:
            perms = get_all_permission_codes()
        else:
            perms = list(role.permissions.values_list('code', flat=True))

        data = role.to_dict()
        data['permissions'] = perms
        return JsonResponse({"status": "success", "role": data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def api_admin_role_save(request):
    """
    Create or Update a Role and its assigned permissions.
    Protected strictly: Only Super Admin can manage roles.
    """
    if not request.admin_user.role or not request.admin_user.role.is_super:
        return JsonResponse({"status": "error", "message": "Only Super Admins can manage roles and permissions."}, status=403)

    try:
        data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST.dict()
        if 'permissions' in request.POST:
            perms_raw = request.POST.getlist('permissions')
        else:
            perms_raw = data.get('permissions', [])
            if isinstance(perms_raw, str):
                try:
                    perms_raw = json.loads(perms_raw)
                except Exception:
                    perms_raw = [p.strip() for p in perms_raw.split(',') if p.strip()]

        role_id = data.get('role_id')
        name = (data.get('name') or '').strip()
        description = (data.get('description') or '').strip()
        is_active = data.get('is_active') in [True, 'true', 'True', '1', 1, 'on']

        if not name:
            return JsonResponse({"status": "error", "message": "Role name is required."}, status=400)

        # Check unique name
        name_exists = Role.objects.filter(name__iexact=name)
        if role_id:
            name_exists = name_exists.exclude(id=role_id)
        if name_exists.exists():
            return JsonResponse({"status": "error", "message": f"A role named '{name}' already exists."}, status=400)

        if role_id:
            # Update existing role
            role = get_object_or_404(Role, id=role_id)
            if role.is_system and role.name != name:
                # System roles keep their canonical names
                name = role.name

            before_perms = set(role.permissions.values_list('code', flat=True))
            role.name = name
            role.description = description
            if not role.is_system:
                role.is_active = is_active
            role.save()

            if not role.is_super:
                # Update permissions
                role.permissions.all().delete()
                new_perms = [RolePermission(role=role, code=c) for c in set(perms_raw)]
                RolePermission.objects.bulk_create(new_perms)

            after_perms = set(perms_raw)
            added = after_perms - before_perms
            removed = before_perms - after_perms
            log_activity("security", "Role Updated", f"Role '{role.name}' updated by {request.admin_user.email}. Added: {len(added)}, Removed: {len(removed)}")
            msg = f"Role '{role.name}' updated successfully."
        else:
            # Create new role
            role = Role.objects.create(
                name=name,
                description=description,
                is_super=False,
                is_system=False,
                is_active=True
            )
            new_perms = [RolePermission(role=role, code=c) for c in set(perms_raw)]
            RolePermission.objects.bulk_create(new_perms)
            log_activity("security", "Role Created", f"New role '{role.name}' created with {len(new_perms)} permissions by {request.admin_user.email}")
            msg = f"Role '{role.name}' created successfully."

        return JsonResponse({"status": "success", "message": msg, "role": role.to_dict()})
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Failed to save role: {str(e)}"}, status=500)


@admin_required
@require_http_methods(["POST"])
def api_admin_role_archive(request, role_id):
    """Archive or restore a role."""
    if not request.admin_user.role or not request.admin_user.role.is_super:
        return JsonResponse({"status": "error", "message": "Only Super Admins can archive roles."}, status=403)

    try:
        role = get_object_or_404(Role, id=role_id)
        if role.is_system:
            return JsonResponse({"status": "error", "message": "System core roles cannot be archived."}, status=400)

        role.is_active = not role.is_active
        role.save(update_fields=['is_active'])

        action_str = "restored" if role.is_active else "archived"
        log_activity("security", "Role Status Changed", f"Role '{role.name}' {action_str} by {request.admin_user.email}")
        return JsonResponse({"status": "success", "message": f"Role '{role.name}' has been {action_str}.", "is_active": role.is_active})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def api_admin_role_duplicate(request, role_id):
    """Duplicate an existing role and its permissions."""
    if not request.admin_user.role or not request.admin_user.role.is_super:
        return JsonResponse({"status": "error", "message": "Only Super Admins can duplicate roles."}, status=403)

    try:
        source_role = get_object_or_404(Role, id=role_id)
        base_name = f"Copy of {source_role.name}"
        target_name = base_name
        counter = 1
        while Role.objects.filter(name=target_name).exists():
            counter += 1
            target_name = f"{base_name} ({counter})"

        new_role = Role.objects.create(
            name=target_name,
            description=f"Cloned from {source_role.name}. {source_role.description}",
            is_super=False,
            is_system=False,
            is_active=True
        )

        # Clone permissions
        if source_role.is_super:
            source_perms = get_all_permission_codes()
        else:
            source_perms = source_role.permissions.values_list('code', flat=True)

        cloned_perms = [RolePermission(role=new_role, code=code) for code in source_perms]
        RolePermission.objects.bulk_create(cloned_perms)

        log_activity("security", "Role Duplicated", f"Role '{new_role.name}' cloned from '{source_role.name}' by {request.admin_user.email}")
        return JsonResponse({
            "status": "success",
            "message": f"Role duplicated as '{new_role.name}'.",
            "role": new_role.to_dict()
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@admin_required
@permission_required("roles.export")
def api_admin_roles_export(request):
    """Export roles list to CSV."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="user_roles_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Role ID', 'Role Name', 'Description', 'System Role', 'Super Admin', 'Active Users Count', 'Permissions Count', 'Status', 'Created Date'])

    for r in Role.objects.annotate(user_count=Count('users'), perm_count=Count('permissions')).order_by('id'):
        writer.writerow([
            r.id,
            r.name,
            r.description,
            'Yes' if r.is_system else 'No',
            'Yes' if r.is_super else 'No',
            r.user_count,
            'ALL (Super)' if r.is_super else r.perm_count,
            'Active' if r.is_active else 'Archived',
            r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else ''
        ])

    return response

