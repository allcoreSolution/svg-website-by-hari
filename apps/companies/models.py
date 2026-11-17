from django.db import models

class CompanyEnquiry(models.Model):
    recruiter_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, blank=True, default="")
    company_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=120)
    address = models.TextField(blank=True, default="")
    job_title = models.CharField(max_length=150, blank=True, default="")
    department = models.CharField(max_length=100, blank=True, default="")
    job_type = models.CharField(max_length=50, blank=True, default="Full Time")
    application_deadline = models.CharField(max_length=50, blank=True, default="30 Days")
    vacancies = models.CharField(max_length=20, default="1")
    experience_req = models.CharField(max_length=100, blank=True, default="")
    salary_range = models.CharField(max_length=100, blank=True, default="")
    requirements = models.TextField(blank=True, default="")
    message = models.TextField(blank=True, default="")
    status = models.CharField(max_length=50, default="New")
    notes = models.TextField(blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'company_enquiries'
        verbose_name = 'Company Enquiry'
        verbose_name_plural = 'Company Enquiries'
        ordering = ['-id']

    def to_dict(self):
        return {
            "id": self.id,
            "recruiter_name": self.recruiter_name,
            "designation": self.designation or "",
            "company_name": self.company_name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address or "",
            "job_title": self.job_title or "",
            "department": self.department or "",
            "job_type": self.job_type or "Full Time",
            "application_deadline": self.application_deadline or "30 Days",
            "vacancies": self.vacancies or "1",
            "experience_req": self.experience_req or "",
            "salary_range": self.salary_range or "",
            "requirements": self.requirements or "",
            "message": self.message or "",
            "status": self.status or "New",
            "notes": self.notes or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

    def __str__(self):
        return f"{self.company_name} - {self.recruiter_name}"


class Company(models.Model):
    name = models.CharField(max_length=150)
    industry = models.CharField(max_length=100, blank=True, default="")
    website = models.CharField(max_length=200, blank=True, default="")
    email = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="Lucknow")
    state = models.CharField(max_length=100, blank=True, default="Uttar Pradesh")
    gst_number = models.CharField(max_length=20, blank=True, default="")
    status = models.CharField(max_length=50, default="Active")
    source_enquiry = models.ForeignKey(CompanyEnquiry, on_delete=models.SET_NULL, null=True, blank=True, related_name="converted_companies")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'companies'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['-id']

    def to_dict(self):
        primary_contact = self.contacts.filter(is_primary=True).first() or self.contacts.first()
        return {
            "id": self.id,
            "name": self.name,
            "industry": self.industry or "",
            "website": self.website or "",
            "email": self.email,
            "phone": self.phone,
            "address": self.address or "",
            "city": self.city or "Lucknow",
            "state": self.state or "Uttar Pradesh",
            "gst_number": self.gst_number or "",
            "status": self.status or "Active",
            "source_enquiry_id": self.source_enquiry_id,
            "notes": self.notes or "",
            "primary_contact_name": primary_contact.name if primary_contact else "",
            "primary_contact_email": primary_contact.email if primary_contact else "",
            "primary_contact_phone": primary_contact.phone if primary_contact else "",
            "contacts_count": self.contacts.count(),
            "requirements_count": self.requirements.count(),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else "",
        }

    def __str__(self):
        return self.name


class CompanyContact(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, blank=True, default="")
    email = models.CharField(max_length=120, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'company_contacts'
        verbose_name = 'Company Contact'
        verbose_name_plural = 'Company Contacts'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if self.is_primary and self.company_id:
            CompanyContact.objects.filter(company_id=self.company_id, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company.name if self.company else "",
            "name": self.name,
            "designation": self.designation or "",
            "email": self.email or "",
            "phone": self.phone or "",
            "is_primary": self.is_primary,
            "notes": self.notes or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

    def __str__(self):
        return f"{self.name} ({self.company.name if self.company else 'N/A'})"


class CompanyRequirement(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="requirements")
    contact = models.ForeignKey(CompanyContact, on_delete=models.SET_NULL, null=True, blank=True, related_name="requirements")
    source_enquiry = models.ForeignKey(CompanyEnquiry, on_delete=models.SET_NULL, null=True, blank=True, related_name="company_requirements")
    job = models.OneToOneField("jobs.Job", on_delete=models.SET_NULL, null=True, blank=True, related_name="requirement")
    title = models.CharField(max_length=150)
    department = models.CharField(max_length=100, blank=True, default="")
    job_type = models.CharField(max_length=50, default="Full Time")
    location = models.CharField(max_length=150, default="Lucknow, UP")
    vacancies = models.CharField(max_length=20, default="1")
    experience_req = models.CharField(max_length=100, blank=True, default="")
    salary_range = models.CharField(max_length=100, blank=True, default="")
    qualification = models.CharField(max_length=150, blank=True, default="")
    description = models.TextField(blank=True, default="")
    requirements = models.TextField(blank=True, default="")
    deadline = models.CharField(max_length=50, blank=True, default="")
    status = models.CharField(max_length=50, default="Active")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'company_requirements'
        verbose_name = 'Company Requirement'
        verbose_name_plural = 'Company Requirements'
        ordering = ['-id']

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company.name if self.company else "",
            "contact_id": self.contact_id,
            "contact_name": self.contact.name if self.contact else "",
            "source_enquiry_id": self.source_enquiry_id,
            "job_id": self.job_id,
            "job_published": bool(self.job_id),
            "title": self.title,
            "department": self.department or "",
            "job_type": self.job_type or "Full Time",
            "location": self.location or "Lucknow, UP",
            "vacancies": self.vacancies or "1",
            "experience_req": self.experience_req or "",
            "salary_range": self.salary_range or "",
            "qualification": self.qualification or "",
            "description": self.description or "",
            "requirements": self.requirements or "",
            "deadline": self.deadline or "",
            "status": self.status or "Active",
            "notes": self.notes or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

    def __str__(self):
        return f"{self.title} - {self.company.name if self.company else 'N/A'}"
