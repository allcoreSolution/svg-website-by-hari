# Data migration to standardize existing Job status values to canonical format
from django.db import migrations


def standardize_job_statuses(apps, schema_editor):
    Job = apps.get_model('jobs', 'Job')
    # Convert all active/live variations to canonical 'LIVE'
    Job.objects.filter(status__in=['Active', 'Live', 'active', 'live']).update(status='LIVE')
    # Convert pending variations to 'PENDING_APPROVAL'
    Job.objects.filter(status__in=['Pending', 'pending', 'pending_approval']).update(status='PENDING_APPROVAL')
    # Convert closed variations to 'CLOSED'
    Job.objects.filter(status__in=['Closed', 'closed']).update(status='CLOSED')
    # Convert expired variations to 'EXPIRED'
    Job.objects.filter(status__in=['Expired', 'expired']).update(status='EXPIRED')
    # Convert draft variations to 'DRAFT'
    Job.objects.filter(status__in=['Draft', 'draft']).update(status='DRAFT')


def reverse_standardize(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0004_alter_job_status_alter_jobcategory_category_type'),
    ]

    operations = [
        migrations.RunPython(standardize_job_statuses, reverse_code=reverse_standardize),
    ]
