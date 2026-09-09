from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from accounts.permissions import HasCustomerRole

from .models import (
    Project,
    ProjectStatusHistory,
)

from .serializers import (
    ProjectSerializer,
    ProjectStatusHistorySerializer,
    WorkerMatchSerializer,
)

from .services import WorkerMatchingService

from accounts.models import User

from .hiring_services import ProjectHiringService
from .models import ProjectWorker
from .serializers import ProjectWorkerSerializer
class ProjectListCreateView(generics.ListCreateAPIView):
    """
    Allows customers to:
    - View their projects
    - Create new projects
    """

    serializer_class = ProjectSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        HasCustomerRole,
    ]

    def get_queryset(self):

        return Project.objects.filter(
            customer=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):

        serializer.save(
            customer=self.request.user
        )


class ProjectDetailView(generics.RetrieveUpdateAPIView):

    serializer_class = ProjectSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        HasCustomerRole,
    ]

    def get_queryset(self):

        return Project.objects.filter(
            customer=self.request.user
        )

    def perform_update(self, serializer):

        project = self.get_object()

        if project.status in [
            Project.ProjectStatus.COMPLETED,
            Project.ProjectStatus.CANCELLED,
        ]:
            raise PermissionDenied(
                "Completed or cancelled projects "
                "cannot be modified."
            )

        previous_status = project.status

        updated_project = serializer.save()

        new_status = updated_project.status

        if previous_status != new_status:

            ProjectStatusHistory.objects.create(
                project=updated_project,
                previous_status=previous_status,
                new_status=new_status,
                changed_by=self.request.user,
            )

class ProjectHistoryView(generics.ListAPIView):

    serializer_class = ProjectStatusHistorySerializer

    permission_classes = [
        permissions.IsAuthenticated,
        HasCustomerRole,
    ]

    def get_queryset(self):

        project_id = self.kwargs["project_id"]

        return ProjectStatusHistory.objects.filter(
            project__id=project_id,
            project__customer=self.request.user
        ).order_by("-changed_at")

class ProjectWorkerMatchesView(generics.GenericAPIView):

    serializer_class = WorkerMatchSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        HasCustomerRole,
    ]

    def get(self, request, project_id):

        try:

            project = Project.objects.get(
                id=project_id,
                customer=request.user
            )

        except Project.DoesNotExist:

            raise PermissionDenied(
                "You do not have access to this project."
            )

        matching_service = WorkerMatchingService(
            project
        )

        matches = matching_service.get_matches()

        serializer = self.get_serializer(
            matches,
            many=True
        )

        return Response(
            serializer.data
        )


class InviteWorkerView(generics.CreateAPIView):

    serializer_class = ProjectWorkerSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def create(self, request, *args, **kwargs):

        project = get_object_or_404(
            Project,
            id=kwargs["project_id"]
        )

        worker_id = request.data.get("worker")

        if not worker_id:

            return Response(
                {
                    "detail": "worker is required."
                },
                status=400
            )

        worker = get_object_or_404(
            User,
            id=worker_id
        )

        assignment = (
            ProjectHiringService.invite_worker(
                project=project,
                worker=worker,
                customer=request.user
            )
        )

        serializer = self.get_serializer(
            assignment
        )

        return Response(
            serializer.data,
            status=201
        )

class WorkerAssignmentStatusView(
    generics.GenericAPIView
):

    serializer_class = ProjectWorkerSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def patch(self, request, assignment_id):

        assignment = get_object_or_404(
            ProjectWorker,
            id=assignment_id
        )

        new_status = request.data.get(
            "status"
        )

        if not new_status:

            return Response(
                {
                    "detail": "status is required."
                },
                status=400
            )

        valid_statuses = [
            choice[0]
            for choice in (
                ProjectWorker.WorkerStatus.choices
            )
        ]

        if new_status not in valid_statuses:

            return Response(
                {
                    "detail": "Invalid worker status."
                },
                status=400
            )

        assignment = (
            ProjectHiringService.update_worker_status(
                assignment=assignment,
                new_status=new_status,
                user=request.user
            )
        )

        serializer = self.get_serializer(
            assignment
        )

        return Response(
            serializer.data
        )

