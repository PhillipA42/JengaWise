from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

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