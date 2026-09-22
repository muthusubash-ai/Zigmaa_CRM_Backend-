from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .employee_serializers import EmployeeReadSerializer, EmployeeWriteSerializer
from .models import Department, Employee, Role, User
from .permissions import HasModulePermission


ROLE_ALIASES = {
    "employee": "Employee",
    "hr": "HR",
    "hr_manager": "HR",
}


def employee_queryset(request):
    queryset = Employee.objects.select_related("user", "user__role", "department").order_by("id")
    if getattr(request, "permission_scope", None) == "own":
        queryset = queryset.filter(user=request.user)
    return queryset


def get_department(value):
    value = str(value or "").strip()
    if not value:
        raise ValueError("Department is required.")
    if value.isdigit():
        department = Department.objects.filter(pk=int(value), is_active=True).first()
    else:
        department = Department.objects.filter(name__iexact=value, is_active=True).first()
    if department is None:
        department, _ = Department.objects.get_or_create(name=value, defaults={"is_active": True})
    return department


def get_role(value):
    role_name = ROLE_ALIASES.get(str(value or "employee").strip().lower(), str(value or "Employee").strip())
    if role_name not in {"Employee", "HR"}:
        raise ValueError("Only Employee or HR roles can be assigned from this form.")
    role = Role.objects.filter(name=role_name, is_active=True).first()
    if role is None:
        raise ValueError(f"{role_name} role is not configured.")
    return role


def next_employee_code():
    last_code = Employee.objects.order_by("-id").values_list("employee_code", flat=True).first()
    try:
        next_number = int(str(last_code or "EMP000").replace("EMP", "")) + 1
    except ValueError:
        next_number = Employee.objects.count() + 1
    code = f"EMP{next_number:03d}"
    while Employee.objects.filter(employee_code=code).exists():
        next_number += 1
        code = f"EMP{next_number:03d}"
    return code


class EmployeeListCreateView(APIView):
    permission_classes = [HasModulePermission]
    permission_module = "employees"

    def get(self, request):
        data = EmployeeReadSerializer(employee_queryset(request), many=True).data
        return Response({"employees": data})

    @transaction.atomic
    def post(self, request):
        serializer = EmployeeWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        email = values["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            return Response({"detail": "An account with this email already exists."}, status=status.HTTP_409_CONFLICT)
        try:
            department = get_department(values["department"])
            role = get_role(values.get("role"))
        except ValueError as error:
            return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            email=email,
            password=values.get("password") or None,
            full_name=values["name"],
            phone=values.get("phone", ""),
            role=role,
        )
        employee = Employee.objects.create(
            user=user,
            department=department,
            employee_code=next_employee_code(),
            designation=values.get("designation", ""),
            date_of_joining=values.get("joining") or timezone.localdate(),
            salary=values.get("salary"),
        )
        return Response(EmployeeReadSerializer(employee).data, status=status.HTTP_201_CREATED)


class EmployeeDetailView(APIView):
    permission_classes = [HasModulePermission]
    permission_module = "employees"

    def get_object(self, request, employee_id):
        return employee_queryset(request).filter(pk=employee_id).first()

    def get(self, request, employee_id):
        employee = self.get_object(request, employee_id)
        if employee is None:
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(EmployeeReadSerializer(employee).data)

    @transaction.atomic
    def patch(self, request, employee_id):
        employee = self.get_object(request, employee_id)
        if employee is None:
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        try:
            if "department" in values:
                employee.department = get_department(values["department"])
            if "designation" in values:
                employee.designation = values["designation"]
            if "joining" in values and values["joining"] is not None:
                employee.date_of_joining = values["joining"]
            if "salary" in values:
                employee.salary = values["salary"]
            if "is_active" in values:
                employee.is_active = values["is_active"]
                employee.user.is_active = values["is_active"]
            if "name" in values:
                employee.user.full_name = values["name"]
            if "phone" in values:
                employee.user.phone = values["phone"]
            if "email" in values and values["email"].lower() != employee.user.email.lower():
                if User.objects.filter(email__iexact=values["email"]).exclude(pk=employee.user_id).exists():
                    return Response({"detail": "An account with this email already exists."}, status=status.HTTP_409_CONFLICT)
                employee.user.email = values["email"].lower()
            if "role" in values:
                employee.user.role = get_role(values["role"])
            if values.get("password"):
                employee.user.set_password(values["password"])
            employee.user.save()
            employee.save()
        except ValueError as error:
            return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(EmployeeReadSerializer(employee).data)

    @transaction.atomic
    def delete(self, request, employee_id):
        employee = self.get_object(request, employee_id)
        if employee is None:
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        employee.is_active = False
        employee.user.is_active = False
        employee.user.save(update_fields=["is_active", "updated_at"])
        employee.save(update_fields=["is_active", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
