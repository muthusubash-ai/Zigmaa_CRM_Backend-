from rest_framework import serializers


class EmployeeWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100)
    phone = serializers.CharField(max_length=20, allow_blank=True, required=False)
    department = serializers.CharField(max_length=100)
    designation = serializers.CharField(max_length=100, allow_blank=True, required=False)
    joining = serializers.DateField(required=False, allow_null=True)
    salary = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    role = serializers.CharField(required=False, default="employee")
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, trim_whitespace=False)
    is_active = serializers.BooleanField(required=False)


class EmployeeReadSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField(source="id")
    id = serializers.CharField(source="employee_code")
    name = serializers.CharField(source="user.full_name")
    email = serializers.EmailField(source="user.email")
    phone = serializers.CharField(source="user.phone")
    department = serializers.CharField(source="department.name")
    designation = serializers.CharField()
    joining = serializers.DateField(source="date_of_joining")
    salary = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    role = serializers.CharField(source="user.role.name")
    status = serializers.SerializerMethodField()

    def get_status(self, employee):
        return "Active" if employee.is_active and employee.user.is_active else "Inactive"
