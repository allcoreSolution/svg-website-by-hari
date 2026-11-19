import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()

# Automatically ensure database migrations and admin setup run on server start
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
    call_command('create_panel_admin')
    
    # Ensure Recruitment & Placement hire talent CTA routes to employer portal
    try:
        from apps.core.models import RecruitmentPlacementSettings
        RecruitmentPlacementSettings.objects.filter(hero_hire_btn_url__in=['#contact', '#', '']).update(hero_hire_btn_url='/employer/hire-talent/')
    except Exception:
        pass
except Exception as e:
    import logging
    logging.getLogger(__name__).warning("Startup auto-migration failed: %s", e)

