from django.utils import timezone
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from werkzeug.security import check_password_hash as check_werkzeug_hash

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, default='')
    is_super = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        ordering = ['name']

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_super': self.is_super,
            'is_system': self.is_system,
            'is_active': self.is_active,
            'users_count': self.users.count() if hasattr(self, 'users') else 0,
            'permissions_count': self.permissions.count() if hasattr(self, 'permissions') else 0,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
        }


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    code = models.CharField(max_length=100)

    class Meta:
        db_table = 'role_permissions'
        unique_together = ('role', 'code')

    def __str__(self):
        return f"{self.role.name} - {self.code}"


class AdminLoginLog(models.Model):
    email = models.CharField(max_length=120)
    ip_address = models.CharField(max_length=50, default='127.0.0.1')
    status = models.CharField(max_length=20, default='success')
    user_agent = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_login_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} ({self.status}) at {self.created_at}"


class AdminUser(models.Model):
    email = models.EmailField(max_length=120, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=100, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    last_login_at = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.CharField(max_length=50, blank=True, default='')
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_admins')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admins'
        verbose_name = 'Admin User'
        verbose_name_plural = 'Admin Users'

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def verify_password(self, raw_password):
        # Support both Django password hash and legacy Werkzeug scrypt hash
        if self.password_hash.startswith(('pbkdf2_', 'argon2', 'bcrypt')):
            return check_password(raw_password, self.password_hash)
        elif self.password_hash.startswith('scrypt:'):
            try:
                valid = check_werkzeug_hash(self.password_hash, raw_password)
                if valid:
                    # Upgrade to Django password hash seamlessly
                    self.set_password(raw_password)
                    self.save(update_fields=['password_hash'])
                return valid
            except Exception:
                return False
        return check_password(raw_password, self.password_hash)

    def get_permission_codes(self):
        if not hasattr(self, '_cached_perms'):
            if not self.is_active or not self.role or not self.role.is_active:
                self._cached_perms = set()
            elif self.role.is_super:
                from .permissions import get_all_permission_codes
                self._cached_perms = set(get_all_permission_codes())
            else:
                self._cached_perms = set(self.role.permissions.values_list('code', flat=True))
        return self._cached_perms

    def has_perm(self, perm_code):
        if not self.is_active:
            return False
        if self.role and self.role.is_super and self.role.is_active:
            return True
        return perm_code in self.get_permission_codes()

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name or self.email.split('@')[0].capitalize(),
            "phone": self.phone or '',
            "role": self.role.name if self.role else 'Unassigned',
            "role_id": self.role_id,
            "is_super": self.role.is_super if self.role else False,
            "is_active": self.is_active,
            "last_login_at": self.last_login_at.strftime('%Y-%m-%d %H:%M:%S') if self.last_login_at else 'Never',
            "last_login_ip": self.last_login_ip or '',
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
        }

    def __str__(self):
        return f"{self.full_name or self.email} ({self.role.name if self.role else 'No Role'})" 


class CandidateAccount(models.Model):
    email = models.EmailField(max_length=120, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=100, blank=True, default="")
    qualification = models.CharField(max_length=150, blank=True, default="")
    experience = models.IntegerField(default=0, blank=True, null=True)
    skills = models.TextField(blank=True, default="")
    current_company = models.CharField(max_length=150, blank=True, default="")
    current_salary = models.CharField(max_length=50, blank=True, default="")
    expected_salary = models.CharField(max_length=50, blank=True, default="")
    availability = models.CharField(max_length=50, blank=True, default="")
    resume = models.CharField(max_length=255, blank=True, default="")
    is_approved = models.BooleanField(default=False)
    approval_status = models.CharField(max_length=20, default='pending')  # 'pending', 'approved', 'rejected'
    rejection_reason = models.TextField(blank=True, null=True, default="")
    email_notifications_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidate_accounts'
        verbose_name = 'Candidate Account'
        verbose_name_plural = 'Candidate Accounts'
        ordering = ['-id']

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def verify_password(self, raw_password):
        return check_password(raw_password, self.password_hash)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "phone": self.phone,
            "city": self.city or "",
            "state": self.state or "",
            "qualification": self.qualification or "",
            "experience": self.experience or 0,
            "skills": self.skills or "",
            "current_company": self.current_company or "",
            "current_salary": self.current_salary or "",
            "expected_salary": self.expected_salary or "",
            "availability": self.availability or "",
            "resume": self.resume or "",
            "is_approved": self.is_approved,
            "approval_status": self.approval_status,
            "rejection_reason": self.rejection_reason or "",
            "email_notifications_enabled": self.email_notifications_enabled,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else "",
        }

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class EmployerAccount(models.Model):
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='employer_accounts')
    company_name = models.CharField(max_length=150)
    contact_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=120, unique=True)
    phone = models.CharField(max_length=20)
    password_hash = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, blank=True, default="")
    company_size = models.CharField(max_length=50, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="Lucknow")
    state = models.CharField(max_length=100, blank=True, default="Uttar Pradesh")
    website = models.CharField(max_length=200, blank=True, default="")
    gst_number = models.CharField(max_length=50, blank=True, default="")
    address = models.TextField(blank=True, default="")
    document = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=20, default='PENDING')  # 'PENDING', 'APPROVED', 'REJECTED', 'SUSPENDED'
    shares_company_data = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True, default="")
    email_notifications_enabled = models.BooleanField(default=True)
    approved_by = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_employers')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employer_accounts'
        verbose_name = 'Employer Account'
        verbose_name_plural = 'Employer Accounts'
        ordering = ['-id']

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def verify_password(self, raw_password):
        return check_password(raw_password, self.password_hash)

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone": self.phone,
            "industry": self.industry or "",
            "company_size": self.company_size or "",
            "city": self.city or "",
            "state": self.state or "",
            "website": self.website or "",
            "gst_number": self.gst_number or "",
            "address": self.address or "",
            "document": self.document or "",
            "status": self.status,
            "shares_company_data": self.shares_company_data,
            "rejection_reason": self.rejection_reason or "",
            "email_notifications_enabled": self.email_notifications_enabled,
            "approved_at": self.approved_at.strftime("%Y-%m-%d %H:%M:%S") if self.approved_at else "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else "",
        }

    def __str__(self):
        return f"{self.company_name} - {self.contact_name} ({self.email})"

class StaffMember(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('On Leave', 'On Leave'),
        ('Inactive', 'Inactive'),
    ]

    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, blank=True, default='')
    phone = models.CharField(max_length=25, blank=True, default='')
    photo = models.CharField(max_length=255, blank=True, default='')
    department = models.CharField(max_length=100, default='IT')
    designation = models.CharField(max_length=150, default='Executive')
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    advance_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    pending_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Active')
    joining_date = models.DateField(blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, default='')
    bank_account_no = models.CharField(max_length=50, blank=True, default='')
    ifsc_code = models.CharField(max_length=30, blank=True, default='')
    pan_number = models.CharField(max_length=30, blank=True, default='')
    aadhaar_number = models.CharField(max_length=30, blank=True, default='')
    address = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'staff_members'
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        try:
            from decimal import Decimal
            self.monthly_salary = Decimal(str(self.monthly_salary or 0))
            self.total_paid = Decimal(str(self.total_paid or 0))
            self.advance_salary = Decimal(str(self.advance_salary or 0))
            
            # If pending_salary is not explicitly provided, calculate remaining
            if self.pending_salary is None:
                rem = self.monthly_salary - (self.total_paid + self.advance_salary)
                self.pending_salary = max(Decimal('0.00'), rem)
            else:
                self.pending_salary = Decimal(str(self.pending_salary or 0))
        except Exception:
            pass
        super().save(*args, **kwargs)

    @property
    def monthly_salary_inr(self):
        try:
            return f"{int(round(float(self.monthly_salary))):,}"
        except Exception:
            return str(self.monthly_salary)

    @property
    def total_paid_inr(self):
        try:
            return f"{int(round(float(self.total_paid))):,}"
        except Exception:
            return str(self.total_paid)

    @property
    def advance_salary_inr(self):
        try:
            return f"{int(round(float(self.advance_salary))):,}"
        except Exception:
            return str(self.advance_salary)

    @property
    def pending_salary_inr(self):
        try:
            return f"{int(round(float(self.pending_salary))):,}"
        except Exception:
            return str(self.pending_salary)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email or '',
            'phone': self.phone or '',
            'photo': self.photo or '',
            'department': self.department,
            'designation': self.designation,
            'monthly_salary': float(self.monthly_salary),
            'total_paid': float(self.total_paid),
            'advance_salary': float(self.advance_salary),
            'pending_salary': float(self.pending_salary),
            'status': self.status,
            'joining_date': self.joining_date.strftime('%Y-%m-%d') if self.joining_date else '',
            'bank_name': self.bank_name,
            'bank_account_no': self.bank_account_no,
            'ifsc_code': self.ifsc_code,
            'pan_number': self.pan_number,
            'aadhaar_number': self.aadhaar_number,
            'address': self.address,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
        }

    def __str__(self):
        return f'{self.full_name} ({self.designation} - {self.department})'


class StaffSalaryPayment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('salary', 'Salary Payment'),
        ('advance', 'Advance Salary'),
        ('bonus', 'Bonus / Incentive'),
        ('deduction', 'Deduction'),
    ]
    staff = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='salary')
    payment_date = models.DateField(default=timezone.now)
    payment_mode = models.CharField(max_length=50, default='Bank Transfer')
    reference_id = models.CharField(max_length=100, blank=True, default='')
    remarks = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'staff_salary_payments'
        ordering = ['-payment_date', '-id']

    def __str__(self):
        return f'{self.staff.full_name} - {self.payment_type} - {self.amount}'

