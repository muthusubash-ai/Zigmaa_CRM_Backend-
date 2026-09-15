from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'roles',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('full_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('phone', models.CharField(max_length=20)),
                ('profile_image', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subordinates', to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='users', to='core.role')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'users',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'departments',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_code', models.CharField(max_length=50, unique=True)),
                ('designation', models.CharField(max_length=100)),
                ('date_of_joining', models.DateField()),
                ('salary', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='core.department')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='employee_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'employees',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('company_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('gst_number', models.CharField(blank=True, max_length=50, null=True)),
                ('address', models.TextField()),
                ('status', models.CharField(default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_clients', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'clients',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quotation_no', models.CharField(max_length=50, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('gst', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('status', models.CharField(default='draft', max_length=20)),
                ('valid_till', models.DateField()),
                ('pdf_file', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quotations', to='core.client')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_quotations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'quotations',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('start_date', models.DateField()),
                ('deadline', models.DateField()),
                ('status', models.CharField(default='planning', max_length=20)),
                ('priority', models.CharField(default='medium', max_length=20)),
                ('progress', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='core.client')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_projects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'projects',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('priority', models.CharField(default='medium', max_length=20)),
                ('status', models.CharField(default='todo', max_length=20)),
                ('start_date', models.DateField()),
                ('due_date', models.DateField()),
                ('completed_at', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_tasks', to=settings.AUTH_USER_MODEL)),
                ('assigned_to', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assigned_tasks', to='core.employee')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='core.project')),
            ],
            options={
                'db_table': 'tasks',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='TaskComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='core.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='task_comments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'task_comments',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='LeaveRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leave_type', models.CharField(max_length=50)),
                ('from_date', models.DateField()),
                ('to_date', models.DateField()),
                ('reason', models.TextField()),
                ('status', models.CharField(default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_leaves', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to='core.employee')),
            ],
            options={
                'db_table': 'leave_requests',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_type', models.CharField(max_length=50)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('date', models.DateField()),
                ('status', models.CharField(default='completed', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_accounts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'accounts',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('related_type', models.CharField(max_length=50)),
                ('related_id', models.BigIntegerField()),
                ('file_name', models.CharField(max_length=255)),
                ('file_path', models.CharField(max_length=255)),
                ('file_type', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='uploaded_documents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'documents',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('related_type', models.CharField(blank=True, max_length=50, null=True)),
                ('related_id', models.BigIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'notifications',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ProjectMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(default='member', max_length=50)),
                ('joined_at', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_memberships', to='core.employee')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='core.project')),
            ],
            options={
                'db_table': 'project_members',
                'ordering': ['id'],
                'unique_together': {('project', 'employee')},
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('check_in', models.TimeField()),
                ('check_out', models.TimeField(blank=True, null=True)),
                ('status', models.CharField(default='present', max_length=20)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='core.employee')),
            ],
            options={
                'db_table': 'attendance',
                'ordering': ['-date'],
                'unique_together': {('employee', 'date')},
            },
        ),
    ]
