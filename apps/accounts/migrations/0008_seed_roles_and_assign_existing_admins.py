from django.db import migrations

def seed_roles_and_permissions(apps, schema_editor):
    Role = apps.get_model('accounts', 'Role')
    RolePermission = apps.get_model('accounts', 'RolePermission')
    AdminUser = apps.get_model('accounts', 'AdminUser')

    from apps.accounts.permissions import DEFAULT_ROLES_PERMISSIONS

    super_admin_role = None

    for role_name, config in DEFAULT_ROLES_PERMISSIONS.items():
        role, _ = Role.objects.get_or_create(
            name=role_name,
            defaults={
                'description': config['description'],
                'is_super': config['is_super'],
                'is_system': config['is_system'],
                'is_active': True,
            }
        )
        if config['is_super']:
            super_admin_role = role

        # Seed permissions
        for perm_code in config['permissions']:
            RolePermission.objects.get_or_create(role=role, code=perm_code)

    # CRITICAL: Every existing AdminUser is assigned to Super Admin role
    if super_admin_role:
        for admin in AdminUser.objects.all():
            admin.role = super_admin_role
            if not admin.full_name:
                admin.full_name = "Super Admin"
            admin.save(update_fields=['role', 'full_name'])


def reverse_seed_roles(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_adminloginlog_role_adminuser_created_by_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_roles_and_permissions, reverse_seed_roles),
    ]

