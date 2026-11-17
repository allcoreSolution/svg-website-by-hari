from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

class ContactEnquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    service = models.CharField(max_length=100, default="General Inquiry")
    message = models.TextField(blank=True, default="")
    enquiry_type = models.CharField(max_length=50, default="General")
    status = models.CharField(max_length=50, default="New")
    notes = models.TextField(blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'contacts'
        verbose_name = 'General Contact Enquiry'
        verbose_name_plural = 'General Contact Enquiries'
        ordering = ['-id']

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "service": self.service,
            "message": self.message or "",
            "enquiry_type": self.enquiry_type or "General",
            "status": self.status or "New",
            "notes": self.notes or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

    def __str__(self):
        return f"{self.name} ({self.service})"


class EnquiryRead(models.Model):
    enquiry_type = models.CharField(max_length=20)  # 'contact', 'company', 'internship'
    enquiry_id = models.IntegerField()
    read_at = models.DateTimeField(auto_now_add=True)
    read_by = models.CharField(max_length=120, blank=True, default="")

    class Meta:
        db_table = 'enquiry_reads'
        verbose_name = 'Enquiry Read Record'
        verbose_name_plural = 'Enquiry Read Records'
        unique_together = ('enquiry_type', 'enquiry_id')
        ordering = ['-id']

    def __str__(self):
        return f"{self.enquiry_type}:{self.enquiry_id} (read by {self.read_by})"


class SubmissionThrottle(models.Model):
    key_hash = models.CharField(max_length=64, db_index=True)
    kind = models.CharField(max_length=20, db_index=True)  # 'ip', 'email', 'phone'
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'submission_throttles'
        verbose_name = 'Submission Throttle'
        verbose_name_plural = 'Submission Throttles'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.kind}:{self.key_hash[:8]} @ {self.timestamp}"


class FollowUp(models.Model):
    contact_person = models.CharField(max_length=100)
    type = models.CharField(max_length=50, default="Candidate")
    phone_or_email = models.CharField(max_length=120, blank=True, default="")
    followup_date = models.CharField(max_length=50, blank=True, default="")
    remarks = models.TextField(blank=True, default="")
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'follow_ups'
        verbose_name = 'Follow Up'
        verbose_name_plural = 'Follow Ups'
        ordering = ['-id']

    def to_dict(self):
        return {
            "id": self.id,
            "contact_person": self.contact_person,
            "type": self.type or "Candidate",
            "phone_or_email": self.phone_or_email or "",
            "followup_date": self.followup_date or "",
            "remarks": self.remarks or "",
            "status": self.status or "Pending",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

    def __str__(self):
        return f"{self.contact_person} ({self.status})"


class ActivityLog(models.Model):
    action_type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    actor = models.CharField(max_length=120, blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'activity_logs'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-id']

    def to_dict(self):
        return {
            "id": self.id,
            "action_type": self.action_type,
            "title": self.title,
            "description": self.description or "",
            "actor": self.actor or "",
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else "",
        }

    def __str__(self):
        return f"{self.action_type}: {self.title}"


def log_activity(action_type, title, description="", actor=""):
    try:
        ActivityLog.objects.create(
            action_type=action_type,
            title=title,
            description=description,
            actor=actor
        )
    except Exception:
        pass


@receiver(post_delete, sender=ContactEnquiry)
def _cleanup_contact_read(sender, instance, **kwargs):
    try:
        EnquiryRead.objects.filter(enquiry_type='contact', enquiry_id=instance.id).delete()
    except Exception:
        pass


def _setup_enquiry_signals():
    try:
        from apps.companies.models import CompanyEnquiry
        @receiver(post_delete, sender=CompanyEnquiry)
        def _cleanup_company_read(sender, instance, **kwargs):
            try:
                EnquiryRead.objects.filter(enquiry_type='company', enquiry_id=instance.id).delete()
            except Exception:
                pass
    except Exception:
        pass

    try:
        from apps.internships.models import InternshipEnquiry
        @receiver(post_delete, sender=InternshipEnquiry)
        def _cleanup_internship_read(sender, instance, **kwargs):
            try:
                EnquiryRead.objects.filter(enquiry_type='internship', enquiry_id=instance.id).delete()
            except Exception:
                pass
    except Exception:
        pass

_setup_enquiry_signals()
