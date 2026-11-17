from django.db import models
from apps.candidates.constants import APPLICATION_FLOW_STEPS, get_candidate_step


class ApplicantQuerySet(models.QuerySet):
    def visible_to_employer(self, employer):
        if not employer:
            return self.none()

        # Approval status MUST be Approved ALWAYS
        approved_q = models.Q(approval_status="Approved")

        # Ownership check: strict job.employer_id == employer.id
        # Fallback to applicant.employer_id ONLY when job is NULL
        # Explicit opt-in via shares_company_data for shared Company
        if getattr(employer, 'shares_company_data', False) and getattr(employer, 'company_id', None):
            ownership_q = (
                models.Q(job__employer_id=employer.id) |
                (models.Q(job__isnull=True) & models.Q(employer_id=employer.id)) |
                models.Q(job__company_id=employer.company_id) |
                (models.Q(job__isnull=True) & models.Q(company_id=employer.company_id))
            )
        else:
            ownership_q = (
                models.Q(job__employer_id=employer.id) |
                (models.Q(job__isnull=True) & models.Q(employer_id=employer.id))
            )

        return self.filter(approved_q).filter(ownership_q)


class ApplicantManager(models.Manager):
    def get_queryset(self):
        return ApplicantQuerySet(self.model, using=self._db)

    def visible_to_employer(self, employer):
        return self.get_queryset().visible_to_employer(employer)


class Applicant(models.Model):
    APPROVAL_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    candidate_account = models.ForeignKey('accounts.CandidateAccount', on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    job = models.ForeignKey('jobs.Job', on_delete=models.SET_NULL, null=True, blank=True, related_name='applicants')
    employer = models.ForeignKey('accounts.EmployerAccount', on_delete=models.SET_NULL, null=True, blank=True, related_name='applicants')
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='applicants')
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=100, blank=True, default="")
    job_title = models.CharField(max_length=150)
    qualification = models.CharField(max_length=150, blank=True, default="")
    experience = models.IntegerField(default=0, blank=True, null=True)
    skills = models.TextField(blank=True, default="")
    current_company = models.CharField(max_length=150, blank=True, default="")
    current_salary = models.CharField(max_length=50, blank=True, default="")
    expected_salary = models.CharField(max_length=50, blank=True, default="")
    availability = models.CharField(max_length=50, blank=True, default="")
    cover_letter = models.TextField(blank=True, default="")
    resume = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=50, default="Application Submitted")
    notes = models.TextField(blank=True, null=True, default="")
    applied_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    # 7-Step Application Flow & Super Admin Approval Fields
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='Pending')
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.CharField(max_length=100, blank=True, default="")
    rejection_reason = models.TextField(blank=True, default="")
    flow_step = models.PositiveSmallIntegerField(default=2)

    objects = ApplicantManager()

    class Meta:
        db_table = 'applicants'
        verbose_name = 'Job Applicant'
        verbose_name_plural = 'Job Applicants'
        ordering = ['-id']

    def to_dict(self):
        emp_name = self.employer.company_name if self.employer else (self.job.employer.company_name if (self.job and self.job.employer) else (self.company.name if self.company else ""))
        return {
            "id": self.id,
            "candidate_account_id": self.candidate_account_id,
            "job_id": self.job_id,
            "employer_id": self.employer_id,
            "company_id": self.company_id,
            "employer_name": emp_name,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "city": self.city or "",
            "state": self.state or "",
            "job_title": self.job_title,
            "qualification": self.qualification or "",
            "experience": self.experience or 0,
            "skills": self.skills or "",
            "current_company": self.current_company or "",
            "current_salary": self.current_salary or "",
            "expected_salary": self.expected_salary or "",
            "availability": self.availability or "",
            "cover_letter": self.cover_letter or "",
            "resume": self.resume or "",
            "status": self.status or "Application Submitted",
            "notes": self.notes or "",
            "applied_on": self.applied_on.strftime("%Y-%m-%d %H:%M:%S") if self.applied_on else "",
            "approval_status": self.approval_status or "Pending",
            "approved_at": self.approved_at.strftime("%Y-%m-%d %H:%M:%S") if self.approved_at else "",
            "approved_by": self.approved_by or "",
            "rejection_reason": self.rejection_reason or "",
            "flow_step": self.flow_step or get_candidate_step(self.status),
            "flow": {
                "step": self.flow_step or get_candidate_step(self.status),
                "status": self.status or "Application Submitted",
                "approval_status": self.approval_status or "Pending",
                "rejection_reason": self.rejection_reason or "",
                "steps": APPLICATION_FLOW_STEPS
            }
        }

    def __str__(self):
        return f"{self.full_name} ({self.job_title})"



class Resume(models.Model):
    full_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    email = models.CharField(max_length=120)
    city = models.CharField(max_length=100, blank=True, default="")
    qualification = models.CharField(max_length=100, blank=True, default="")
    experience = models.CharField(max_length=50, blank=True, default="")
    applying_for = models.CharField(max_length=150, blank=True, default="")
    message = models.TextField(blank=True, default="")
    resume = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=50, default="New")
    notes = models.TextField(blank=True, null=True, default="")
    uploaded_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'resumes'
        verbose_name = 'Quick Resume'
        verbose_name_plural = 'Quick Resumes'
        ordering = ['-id']

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "mobile": self.mobile,
            "email": self.email,
            "city": self.city or "",
            "qualification": self.qualification or "",
            "experience": self.experience or "",
            "applying_for": self.applying_for or "",
            "message": self.message or "",
            "resume": self.resume or "",
            "status": self.status or "New",
            "notes": self.notes or "",
            "uploaded_on": self.uploaded_on.strftime("%Y-%m-%d %H:%M:%S") if self.uploaded_on else "",
        }

    def __str__(self):
        return f"{self.full_name} ({self.applying_for or 'General'})"


class Interview(models.Model):
    candidate_type = models.CharField(max_length=20, default='applicant')
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, null=True, blank=True, related_name='interviews')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, null=True, blank=True, related_name='interviews')
    candidate_id = models.IntegerField(null=True, blank=True)
    candidate_name = models.CharField(max_length=120)
    candidate_email = models.CharField(max_length=120)
    candidate_phone = models.CharField(max_length=20, blank=True, default="")
    job_title = models.CharField(max_length=150, blank=True, default="")
    interview_date = models.DateField()
    interview_time = models.TimeField()
    interview_mode = models.CharField(max_length=100, default="In-Person Office Interview")
    location_or_link = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=50, default="Scheduled")
    result = models.CharField(max_length=50, blank=True, default="")
    feedback = models.TextField(blank=True, default="")
    cancel_reason = models.TextField(blank=True, default="")
    interviewer_notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interviews'
        verbose_name = 'Interview'
        verbose_name_plural = 'Interviews'
        ordering = ['-interview_date', '-interview_time']

    def is_overdue(self):
        from django.utils import timezone
        if self.status in ['Scheduled', 'Rescheduled'] and self.interview_date:
            return self.interview_date < timezone.now().date()
        return False

    def get_candidate_object(self):
        if self.applicant:
            return self.applicant
        if self.resume:
            return self.resume
        if self.candidate_type == 'applicant' and self.candidate_id:
            return Applicant.objects.filter(id=self.candidate_id).first()
        if self.candidate_type == 'resume' and self.candidate_id:
            return Resume.objects.filter(id=self.candidate_id).first()
        return None

    def to_dict(self):
        obj = self.get_candidate_object()
        candidate_info = obj.to_dict() if obj else {}
        return {
            "id": self.id,
            "candidate_type": self.candidate_type,
            "candidate_id": self.candidate_id or (self.applicant_id if self.candidate_type == 'applicant' else self.resume_id),
            "applicant_id": self.applicant_id,
            "resume_id": self.resume_id,
            "candidate_name": self.candidate_name,
            "candidate_email": self.candidate_email,
            "candidate_phone": self.candidate_phone,
            "job_title": self.job_title,
            "interview_date": self.interview_date.strftime("%Y-%m-%d") if self.interview_date else "",
            "interview_time": self.interview_time.strftime("%H:%M") if self.interview_time else "",
            "interview_mode": self.interview_mode,
            "location_or_link": self.location_or_link or "",
            "status": self.status,
            "result": self.result or "",
            "feedback": self.feedback or "",
            "cancel_reason": self.cancel_reason or "",
            "interviewer_notes": self.interviewer_notes or "",
            "is_overdue": self.is_overdue(),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else "",
            "candidate": candidate_info
        }

    def __str__(self):
        return f"Interview: {self.candidate_name} ({self.interview_date} {self.interview_time})"

