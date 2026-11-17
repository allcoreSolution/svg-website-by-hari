from django.db import models

class JobQuerySet(models.QuerySet):
    def live(self):
        return self.filter(status__in=Job.LIVE_STATUSES)

    def pending(self):
        return self.filter(status__in=Job.PENDING_STATUSES)

    def closed(self):
        return self.filter(status__in=Job.CLOSED_STATUSES)


class Job(models.Model):
    # Canonical Job Statuses
    STATUS_DRAFT = 'DRAFT'
    STATUS_PENDING_APPROVAL = 'PENDING_APPROVAL'
    STATUS_LIVE = 'LIVE'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CLOSED = 'CLOSED'
    STATUS_EXPIRED = 'EXPIRED'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PENDING_APPROVAL, 'Pending Approval'),
        (STATUS_LIVE, 'Live'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_CLOSED, 'Closed'),
        (STATUS_EXPIRED, 'Expired'),
    ]

    # Canonical status groups (with legacy values for backwards compatibility)
    LIVE_STATUSES = ['LIVE', 'Active', 'Live', 'active', 'live']
    PENDING_STATUSES = ['PENDING_APPROVAL', 'Pending', 'pending', 'DRAFT', 'Draft', 'draft']
    CLOSED_STATUSES = ['CLOSED', 'Closed', 'closed', 'EXPIRED', 'Expired', 'expired']

    employer = models.ForeignKey('accounts.EmployerAccount', on_delete=models.SET_NULL, null=True, blank=True, related_name='posted_jobs')
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True, default="")
    department = models.CharField(max_length=100, blank=True, default="")
    location = models.CharField(max_length=150, default="Lucknow, UP")
    employment_type = models.CharField(max_length=50, default="Full Time")
    experience = models.CharField(max_length=50, blank=True, default="")
    salary = models.CharField(max_length=100, blank=True, default="")
    vacancies = models.CharField(max_length=20, default="1")
    qualification = models.CharField(max_length=150, blank=True, default="")
    description = models.TextField(blank=True, default="")
    requirements = models.TextField(blank=True, default="")
    deadline = models.CharField(max_length=50, blank=True, default="")
    status = models.CharField(max_length=50, default=STATUS_LIVE, choices=STATUS_CHOICES)
    rejection_reason = models.TextField(blank=True, null=True, default="")
    approved_by = models.ForeignKey('accounts.AdminUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_jobs')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = JobQuerySet.as_manager()

    class Meta:
        db_table = 'jobs'
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-id']

    def to_dict(self):
        return {
            "id": self.id,
            "employer_id": self.employer_id,
            "employer_name": self.employer.company_name if self.employer else (self.company.name if self.company else ""),
            "company_id": self.company_id,
            "company_name": self.company.name if self.company else (self.employer.company_name if self.employer else ""),
            "title": self.title,
            "category": self.category,
            "department": self.department,
            "location": self.location,
            "employment_type": self.employment_type,
            "experience": self.experience,
            "salary": self.salary,
            "vacancies": self.vacancies,
            "qualification": self.qualification or "",
            "description": self.description,
            "requirements": self.requirements,
            "deadline": self.deadline or "",
            "status": self.status,
            "rejection_reason": self.rejection_reason or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

    def __str__(self):
        return f"{self.title} ({self.location})"


class JobCategory(models.Model):
    CATEGORY_TYPES = [
        ('job_pill', 'Job Pill (Top Marquee)'),
        ('industry', 'Industries We Serve'),
        ('job_category', 'Job Category (Career Tracks)'),
        ('job_type', 'Job Type (Employment / Work Mode)'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=150)
    category_type = models.CharField(max_length=50, choices=CATEGORY_TYPES, default='job_category', db_index=True)
    icon = models.CharField(max_length=100, default='fa-solid fa-briefcase', help_text="FontAwesome / Tabler icon class e.g. fa-solid fa-code")
    badge_color = models.CharField(max_length=50, blank=True, default='t-indigo', help_text="Color class e.g. t-indigo, t-amber, t-teal, t-red")
    count_label = models.CharField(max_length=100, blank=True, default='', help_text="e.g. '2,540 openings' or '245 Jobs'")
    field_slug = models.CharField(max_length=100, blank=True, default='', help_text="Slug for ?field=slug filter")
    link_url = models.CharField(max_length=255, blank=True, default='', help_text="Custom URL link if needed")
    order = models.IntegerField(default=0, help_text="Display order sequence")
    status = models.CharField(max_length=20, default='Active', choices=STATUS_CHOICES, db_index=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_categories'
        verbose_name = 'Job Category'
        verbose_name_plural = 'Job Categories'
        ordering = ['order', 'id']

    def save(self, *args, **kwargs):
        if not self.field_slug and self.name:
            import re
            cleaned = re.sub(r'[^a-zA-Z0-9]+', '', self.name.lower())
            self.field_slug = cleaned or 'general'
        super().save(*args, **kwargs)

    def get_link(self):
        if self.link_url:
            return self.link_url
        if self.field_slug:
            return f"/jobs/?field={self.field_slug}#{self.field_slug}"
        return "#"

    @property
    def icon_class(self):
        return self.icon or 'fas fa-briefcase'

    def get_count_display(self):
        if self.count_label:
            return self.count_label
        if self.field_slug:
            cnt = Job.objects.filter(
                models.Q(category__icontains=self.name) |
                models.Q(category__icontains=self.field_slug) |
                models.Q(department__icontains=self.field_slug),
                status__in=Job.LIVE_STATUSES
            ).count()
            if cnt > 0:
                return f"{cnt} Jobs"
        return "Openings Available"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category_type": self.category_type,
            "category_type_display": self.get_category_type_display(),
            "icon": self.icon,
            "badge_color": self.badge_color,
            "count_label": self.count_label,
            "count_display": self.get_count_display(),
            "field_slug": self.field_slug,
            "link_url": self.link_url,
            "link": self.get_link(),
            "order": self.order,
            "status": self.status,
            "description": self.description,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


