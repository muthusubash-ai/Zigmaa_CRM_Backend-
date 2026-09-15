from decimal import Decimal

from django.db.models import DecimalField, Q, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Account, Employee, LeaveRequest, Project, Task
from .permissions import IsSuperAdmin


COMPLETED_TASK_STATUSES = Q(status__iexact="completed") | Q(status__iexact="done")


class SuperAdminDashboardView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        today = timezone.localdate()

        today_revenue = (
            Account.objects.filter(date=today, status__iexact="completed")
            .filter(Q(account_type__iexact="income") | Q(account_type__iexact="revenue"))
            .aggregate(
                total=Coalesce(
                    Sum("amount"),
                    Decimal("0.00"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )["total"]
        )

        recent_tasks = (
            Task.objects.select_related("assigned_to__user", "project")
            .order_by("-updated_at")[:6]
        )

        return Response(
            {
                "date": today.isoformat(),
                "metrics": {
                    "today_tasks": Task.objects.filter(due_date=today).count(),
                    "completed_tasks": Task.objects.filter(COMPLETED_TASK_STATUSES).count(),
                    "today_revenue": str(today_revenue),
                    "active_projects": Project.objects.exclude(
                        status__in=["completed", "cancelled"]
                    ).count(),
                    "total_employees": Employee.objects.filter(is_active=True).count(),
                    "pending_leaves": LeaveRequest.objects.filter(status__iexact="pending").count(),
                    "overdue_tasks": Task.objects.filter(due_date__lt=today)
                    .exclude(COMPLETED_TASK_STATUSES)
                    .count(),
                },
                "recent_tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "status": task.status,
                        "priority": task.priority,
                        "due_date": task.due_date.isoformat(),
                        "assignee": task.assigned_to.user.full_name,
                        "project": task.project.name if task.project else None,
                    }
                    for task in recent_tasks
                ],
            }
        )
