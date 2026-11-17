from django.db import migrations

def seed_templates(apps, schema_editor):
    MessageTemplate = apps.get_model('communication', 'MessageTemplate')
    templates = [
        {
            "name": "Registration Welcome (Candidate)",
            "audience_type": "candidate",
            "subject": "Welcome to Sky Vision Group Consultancy!",
            "body": "<p>Dear <b>Candidate</b>,</p><p>Welcome to Sky Vision Group Consultancy! Your candidate profile has been registered in our talent network.</p><p>You can now explore active job opportunities, track application statuses, and receive interview invitations directly through your portal dashboard.</p><p>Best regards,<br><b>Sky Vision Group Talent Team</b></p>",
            "is_active": True,
        },
        {
            "name": "Application Shortlisted",
            "audience_type": "candidate",
            "subject": "Congratulations! Your Job Application has been Shortlisted",
            "body": "<p>Dear <b>Candidate</b>,</p><p>We are delighted to inform you that your application for the job position has been <b>Shortlisted</b>!</p><p>Our recruitment team is coordinating with the hiring managers to schedule the upcoming interview round. Please ensure your contact details and resume are up to date in your dashboard.</p><p>Best regards,<br><b>Sky Vision Recruitment Team</b></p>",
            "is_active": True,
        },
        {
            "name": "Selected – Congratulations",
            "audience_type": "candidate",
            "subject": "Congratulations! Job Selection Update",
            "body": "<p>Dear <b>Candidate</b>,</p><p>Congratulations! We are thrilled to share that you have been <b>Selected</b> for the position with our partner company.</p><p>Formal offer documentation and joining instructions will be shared shortly. Please review your portal messages for onboarding details.</p><p>Warm wishes,<br><b>Sky Vision Placement Division</b></p>",
            "is_active": True,
        },
        {
            "name": "Interview Invitation",
            "audience_type": "candidate",
            "subject": "Interview Invitation from Sky Vision Group",
            "body": "<p>Dear <b>Candidate</b>,</p><p>You have been invited for an interview for your applied position with our partner company.</p><p><b>Interview Details & Instructions:</b></p><ul><li>Please be available at the scheduled time.</li><li>Keep a soft copy of your updated resume and identity proof handy.</li><li>Ensure a quiet environment with a stable internet connection if attending virtually.</li></ul><p>We wish you the very best!</p><p>Best regards,<br><b>Sky Vision HR & Hiring Team</b></p>",
            "is_active": True,
        },
        {
            "name": "Document Request",
            "audience_type": "candidate",
            "subject": "Urgent Document Verification Request",
            "body": "<p>Dear <b>Candidate</b>,</p><p>To proceed with your application, we request you to submit the following verification documents:</p><ul><li>Updated Resume / CV</li><li>Educational Certificates</li><li>Previous Employment Relieving Letters / Experience Certificates (if applicable)</li><li>Valid Photo ID (Aadhaar / PAN / Passport)</li></ul><p>Please upload them to your candidate portal or reply to this notice promptly.</p><p>Sincerely,<br><b>Sky Vision Verification Team</b></p>",
            "is_active": True,
        },
        {
            "name": "General Announcement (Candidates)",
            "audience_type": "candidate",
            "subject": "Important Update from Sky Vision Group for Candidates",
            "body": "<p>Dear <b>Candidate</b>,</p><p>We would like to share an important announcement regarding upcoming recruitment drives and employment opportunities through Sky Vision Group.</p><p>Please log in to your candidate dashboard regularly to discover newly added verified vacancies.</p><p>Warm regards,<br><b>Sky Vision Group Management</b></p>",
            "is_active": True,
        },
        {
            "name": "General Announcement (Employers)",
            "audience_type": "employer",
            "subject": "Sky Vision Group Partner Announcement & Talent Updates",
            "body": "<p>Dear <b>Partner</b>,</p><p>We hope this message finds you well. As part of our continuous commitment to supplying exceptional talent to <b>your organization</b>, we are pleased to announce our latest pipeline of pre-screened and certified candidates.</p><p>Log in to your employer portal to review matched candidate profiles and schedule candidate interviews.</p><p>Thank you for partnering with us,<br><b>Sky Vision Corporate Relations</b></p>",
            "is_active": True,
        },
    ]

    for tpl in templates:
        MessageTemplate.objects.get_or_create(
            name=tpl["name"],
            defaults=tpl
        )

def unseed_templates(apps, schema_editor):
    MessageTemplate = apps.get_model('communication', 'MessageTemplate')
    MessageTemplate.objects.filter(name__in=[
        "Registration Welcome (Candidate)",
        "Application Shortlisted",
        "Selected – Congratulations",
        "Interview Invitation",
        "Document Request",
        "General Announcement (Candidates)",
        "General Announcement (Employers)",
    ]).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0004_messagetemplate_bulkmessage_attachment_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_templates, unseed_templates),
    ]
