from django.db import models
from django.utils import timezone


class BulkMessage(models.Model):
    AUDIENCE_CHOICES = [
        ('candidate', 'Candidate'),
        ('employer', 'Employer'),
    ]

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Sending', 'Sending'),
        ('Sent', 'Sent'),
        ('Partial', 'Partial'),
        ('Failed', 'Failed'),
        ('Stopped', 'Stopped'),
        ('Interrupted', 'Interrupted'),
    ]

    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    audience_type = models.CharField(max_length=20, choices=AUDIENCE_CHOICES)
    candidate_filter = models.CharField(max_length=50, blank=True, default='')  # 'registered', 'shortlisted', 'selected', ''
    include_pending = models.BooleanField(default=False)
    employer_ids = models.JSONField(default=list, blank=True)
    candidate_ids = models.JSONField(default=list, blank=True)
    job_id = models.IntegerField(null=True, blank=True)
    company_id = models.IntegerField(null=True, blank=True)
    channels = models.JSONField(default=list)  # ['dashboard', 'email', 'sms', 'whatsapp']
    attachment = models.FileField(upload_to='uploads/communication/', null=True, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True, default='', db_index=True)
    created_by = models.ForeignKey(
        'accounts.AdminUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bulk_messages'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    skipped_count = models.IntegerField(default=0)
    pending_count = models.IntegerField(default=0)
    last_activity_at = models.DateTimeField(null=True, blank=True)
    is_stopped = models.BooleanField(default=False)
    stop_reason = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'bulk_messages'
        verbose_name = 'Bulk Message'
        verbose_name_plural = 'Bulk Messages'
        ordering = ['-id']

    def __str__(self):
        return f"{self.title} ({self.audience_type} - {self.status})"


class MessageRecipient(models.Model):
    CHANNEL_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
    ]

    DELIVERY_CHOICES = [
        ('Pending', 'Pending'),
        ('Sent', 'Sent'),
        ('Failed', 'Failed'),
        ('Skipped', 'Skipped'),
    ]

    bulk_message = models.ForeignKey(
        BulkMessage,
        on_delete=models.CASCADE,
        related_name='recipients'
    )
    candidate_account = models.ForeignKey(
        'accounts.CandidateAccount',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='received_messages'
    )
    employer_account = models.ForeignKey(
        'accounts.EmployerAccount',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='received_messages'
    )
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='Pending')
    error = models.TextField(blank=True, default='')
    sent_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'message_recipients'
        verbose_name = 'Message Recipient'
        verbose_name_plural = 'Message Recipients'
        constraints = [
            models.UniqueConstraint(
                fields=['bulk_message', 'candidate_account', 'channel'],
                condition=models.Q(candidate_account__isnull=False),
                name='unique_candidate_recipient_per_channel'
            ),
            models.UniqueConstraint(
                fields=['bulk_message', 'employer_account', 'channel'],
                condition=models.Q(employer_account__isnull=False),
                name='unique_employer_recipient_per_channel'
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(candidate_account__isnull=False, employer_account__isnull=True) |
                    models.Q(candidate_account__isnull=True, employer_account__isnull=False)
                ),
                name='message_recipient_exactly_one_account'
            ),
        ]
        indexes = [
            models.Index(fields=['candidate_account', 'is_read']),
            models.Index(fields=['employer_account', 'is_read']),
        ]
        ordering = ['-id']

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def __str__(self):
        target = self.candidate_account or self.employer_account
        return f"Recipient {target} via {self.channel} ({self.delivery_status})"


class MessageTemplate(models.Model):
    AUDIENCE_CHOICES = [
        ('candidate', 'Candidate'),
        ('employer', 'Employer'),
        ('all', 'All Audiences'),
    ]

    name = models.CharField(max_length=150)
    audience_type = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='candidate')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'message_templates'
        verbose_name = 'Message Template'
        verbose_name_plural = 'Message Templates'
        ordering = ['-id']

    def __str__(self):
        return f"{self.name} ({self.audience_type})"

