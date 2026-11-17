from django.db import models

class InternshipEnquiry(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    college = models.CharField(max_length=150, blank=True, default="")
    course_stream = models.CharField(max_length=100)
    duration = models.CharField(max_length=50, default="3 Months")
    skills = models.TextField(blank=True, default="")
    message = models.TextField(blank=True, default="")
    resume = models.CharField(max_length=255, blank=True, null=True, default="")
    status = models.CharField(max_length=50, default="New")
    notes = models.TextField(blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'internship_enquiries'
        verbose_name = 'Internship Enquiry'
        verbose_name_plural = 'Internship Enquiries'
        ordering = ['-id']

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "college": self.college or "",
            "course_stream": self.course_stream or "",
            "duration": self.duration or "3 Months",
            "skills": self.skills or "",
            "message": self.message or "",
            "resume": self.resume or "",
            "status": self.status or "New",
            "notes": self.notes or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

    def __str__(self):
        return f"{self.full_name} ({self.course_stream})"


class InternshipProvider(models.Model):
    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100, blank=True, default="")
    email = models.CharField(max_length=120, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    industry = models.CharField(max_length=100, blank=True, default="")
    address = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'internship_providers'
        verbose_name = 'Internship Provider'
        verbose_name_plural = 'Internship Providers'
        ordering = ['-id']

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "contact_person": self.contact_person or "",
            "email": self.email or "",
            "phone": self.phone or "",
            "industry": self.industry or "",
            "address": self.address or "",
            "notes": self.notes or "",
            "is_active": self.is_active,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

    def __str__(self):
        return self.name


class Internship(models.Model):
    title = models.CharField(max_length=150)
    provider = models.ForeignKey(InternshipProvider, on_delete=models.SET_NULL, null=True, blank=True, related_name='internships')
    description = models.TextField(blank=True, default="")
    location = models.CharField(max_length=100, blank=True, default="")
    mode = models.CharField(max_length=50, default="Onsite")
    duration = models.CharField(max_length=50, default="3 Months")
    stipend = models.CharField(max_length=50, blank=True, default="")
    seats = models.PositiveIntegerField(default=1)
    skills_required = models.TextField(blank=True, default="")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, default="Open")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'internships'
        verbose_name = 'Internship'
        verbose_name_plural = 'Internships'
        ordering = ['-id']

    def to_dict(self):
        apps_count = self.applications.count() if hasattr(self, 'applications') else 0
        sel_count = self.applications.filter(status='Selected').count() if hasattr(self, 'applications') else 0
        return {
            "id": self.id,
            "title": self.title,
            "provider_id": self.provider_id,
            "provider_name": self.provider.name if self.provider else "Sky Vision Consultancy",
            "description": self.description or "",
            "location": self.location or "",
            "mode": self.mode or "Onsite",
            "duration": self.duration or "3 Months",
            "stipend": self.stipend or "",
            "seats": self.seats,
            "skills_required": self.skills_required or "",
            "start_date": self.start_date.strftime("%Y-%m-%d") if self.start_date else "",
            "end_date": self.end_date.strftime("%Y-%m-%d") if self.end_date else "",
            "status": self.status or "Open",
            "applications_count": apps_count,
            "selected_count": sel_count,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else "",
        }

    def __str__(self):
        return f"{self.title} ({self.status})"


class InternshipApplication(models.Model):
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='applications')
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    college = models.CharField(max_length=150, blank=True, default="")
    course_stream = models.CharField(max_length=100, blank=True, default="")
    skills = models.TextField(blank=True, default="")
    message = models.TextField(blank=True, default="")
    resume = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=50, default="Pending")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'internship_applications'
        verbose_name = 'Internship Application'
        verbose_name_plural = 'Internship Applications'
        ordering = ['-id']

    def to_dict(self):
        return {
            "id": self.id,
            "internship_id": self.internship_id,
            "internship_title": self.internship.title if self.internship else "",
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "college": self.college or "",
            "course_stream": self.course_stream or "",
            "skills": self.skills or "",
            "message": self.message or "",
            "resume": self.resume or "",
            "status": self.status or "Pending",
            "notes": self.notes or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

    def __str__(self):
        return f"{self.full_name} - {self.internship.title if self.internship else 'N/A'}"

