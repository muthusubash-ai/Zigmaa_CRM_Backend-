from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        ordering = ['id']

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # Get or create Super Admin role
        super_admin_role, _ = Role.objects.get_or_create(
            name='Super Admin',
            defaults={'description': 'Full system access'}
        )
        extra_fields.setdefault('role', super_admin_role)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='users')
    manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates'
    )
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    google_sub = models.CharField(max_length=255, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20)
    profile_image = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone']

    class Meta:
        db_table = 'users'
        ordering = ['id']

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        ordering = ['id']

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile'
    )
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')
    employee_code = models.CharField(max_length=50, unique=True)
    designation = models.CharField(max_length=100)
    date_of_joining = models.DateField()
    salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'
        ordering = ['id']

    def __str__(self):
        return f"{self.employee_code} - {self.user.full_name}"


class Client(models.Model):
    name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20)
    gst_number = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField()
    status = models.CharField(max_length=20, default='active')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_clients'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clients'
        ordering = ['id']

    def __str__(self):
        return f"{self.name} ({self.company_name})"


class Quotation(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='quotations')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_quotations'
    )
    quotation_no = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    gst = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default='draft')
    valid_till = models.DateField()
    pdf_file = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quotations'
        ordering = ['id']

    def __str__(self):
        return f"Quote #{self.quotation_no} - {self.client.company_name}"


class Project(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    deadline = models.DateField()
    status = models.CharField(max_length=20, default='planning')
    priority = models.CharField(max_length=20, default='medium')
    progress = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['id']

    def __str__(self):
        return self.name


class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='project_memberships'
    )
    role = models.CharField(max_length=50, default='member')
    joined_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_members'
        unique_together = ('project', 'employee')
        ordering = ['id']

    def __str__(self):
        return f"{self.employee.user.full_name} in {self.project.name}"


class Task(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks'
    )
    assigned_to = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name='assigned_tasks'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_tasks'
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=20, default='medium')
    status = models.CharField(max_length=20, default='todo')
    start_date = models.DateField()
    due_date = models.DateField()
    completed_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tasks'
        ordering = ['id']

    def __str__(self):
        return self.title


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='task_comments'
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_comments'
        ordering = ['id']

    def __str__(self):
        return f"Comment by {self.user.full_name} on Task #{self.task_id}"


class Attendance(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='attendance_records'
    )
    date = models.DateField()
    check_in = models.TimeField()
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='present')
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendance'
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.employee_code} - {self.date}"


class LeaveRequest(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='leave_requests'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves',
    )
    leave_type = models.CharField(max_length=50)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leave_requests'
        ordering = ['-id']

    def __str__(self):
        return f"{self.employee.employee_code} - {self.leave_type} ({self.status})"


class Account(models.Model):
    account_type = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    date = models.DateField()
    status = models.CharField(max_length=20, default='completed')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_accounts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts'
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} ({self.account_type}): {self.amount}"


class Document(models.Model):
    related_type = models.CharField(max_length=50)
    related_id = models.BigIntegerField()
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='uploaded_documents'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documents'
        ordering = ['-id']

    def __str__(self):
        return f"{self.file_name} ({self.related_type} #{self.related_id})"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_type = models.CharField(max_length=50, null=True, blank=True)
    related_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-id']

    def __str__(self):
        return f"Notification for {self.user.full_name}: {self.title}"
