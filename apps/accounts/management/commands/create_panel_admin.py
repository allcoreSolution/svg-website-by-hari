import os
from django.core.management.base import BaseCommand
from apps.accounts.models import AdminUser, Role


class Command(BaseCommand):
    help = "Create or update super admin user for admin panel using ADMIN_EMAIL and ADMIN_PASSWORD environment variables."

    def handle(self, *args, **options):
        email = os.environ.get("ADMIN_EMAIL", "").strip().lower() or "harilal@gmail.com"
        password = os.environ.get("ADMIN_PASSWORD", "").strip() or "Admin@123"

        super_role = Role.objects.filter(is_super=True).first()
        if not super_role:
            super_role = Role.objects.filter(name__iexact="Super Admin").first()
            if not super_role:
                super_role = Role.objects.create(
                    name="Super Admin",
                    description="Full administrative access across all modules.",
                    is_super=True,
                    is_system=True,
                    is_active=True,
                )

        admin_user, created = AdminUser.objects.get_or_create(
            email=email,
            defaults={
                "full_name": "Super Admin",
                "is_active": True,
                "role": super_role,
            },
        )

        if not created:
            admin_user.full_name = "Super Admin"
            admin_user.is_active = True
            if super_role:
                admin_user.role = super_role
        elif super_role and not admin_user.role:
            admin_user.role = super_role

        admin_user.set_password(password)
        admin_user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(f"{action} panel admin user '{email}'.")
        )

