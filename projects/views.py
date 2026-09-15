from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .completion_services import ProjectCompletionService
from .hiring_services import ProjectHiringService
from .services import WorkerMatchingService

from accounts.permissions import HasCustomerRole
from accounts.models import User

from .models import (
    Project,
    ProjectStatusHistory,
    ProjectMilestone,
    ProjectPassport,
    ProjectWorker,
    ProjectActivity,
    MarketLocation,
    ConstructionMaterial,
    MaterialPriceObservation,
    LabourRateObservation,
    CostEstimate,
)

from .serializers import (
    ProjectSerializer,
    ProjectStatusHistorySerializer,
    WorkerMatchSerializer,
    ProjectMilestoneSerializer,
    ProjectPassportSerializer,
    ProjectWorkerSerializer,
    ProjectActivitySerializer,
    MarketLocationSerializer,
    SupplierProfileSerializer,
    ConstructionMaterialSerializer,
    MaterialPriceObservationSerializer,
    LabourRateObservationSerializer,
    CostEstimateSerializer,
)


# ============================================================
# PROJECT MANAGEMENT
# ============================================================

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
                "Completed or cancelled projects cannot be modified."
            )

        previous_status = project.status

        updated_project = serializer.save()

        new_status = updated_project.status

        if previous_status != new_status:

            ProjectStatusHistory.objects.create(
                project=updated_project,
                old_status=previous_status,
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
        ).order_by("-created_at")


# ============================================================
# WORKER MATCHING
# ============================================================

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

        matching_service = WorkerMatchingService(project)

        matches = matching_service.get_matches()

        serializer = self.get_serializer(
            matches,
            many=True
        )

        return Response(serializer.data)


# ============================================================
# WORKER HIRING
# ============================================================

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

        assignment = ProjectHiringService.invite_worker(
            project=project,
            worker=worker,
            customer=request.user
        )

        serializer = self.get_serializer(assignment)

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

        new_status = request.data.get("status")

        if not new_status:
            return Response(
                {
                    "detail": "status is required."
                },
                status=400
            )

        valid_statuses = [
            choice[0]
            for choice in ProjectWorker.WorkerStatus.choices
        ]

        if new_status not in valid_statuses:
            return Response(
                {
                    "detail": "Invalid worker status."
                },
                status=400
            )

        assignment = ProjectHiringService.update_worker_status(
            assignment=assignment,
            new_status=new_status,
            user=request.user
        )

        serializer = self.get_serializer(assignment)

        return Response(serializer.data)


# ============================================================
# PROJECT COMPLETION
# ============================================================

class CompleteProjectView(generics.GenericAPIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = ProjectSerializer

    def post(self, request, project_id):

        project = get_object_or_404(
            Project,
            id=project_id
        )

        notes = request.data.get(
            "notes",
            ""
        )

        project = ProjectCompletionService.complete_project(
            project=project,
            customer=request.user,
            notes=notes
        )

        serializer = self.get_serializer(project)

        return Response(
            serializer.data,
            status=200
        )


# ============================================================
# PROJECT MILESTONES
# ============================================================

class ProjectMilestoneListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = ProjectMilestoneSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):

        project = get_object_or_404(
            Project,
            id=self.kwargs["project_id"]
        )

        is_customer = project.customer == self.request.user

        is_assigned_worker = ProjectWorker.objects.filter(
            project=project,
            worker=self.request.user,
            status__in=[
                ProjectWorker.WorkerStatus.ACCEPTED,
                ProjectWorker.WorkerStatus.ACTIVE,
                ProjectWorker.WorkerStatus.COMPLETED,
            ]
        ).exists()

        if not is_customer and not is_assigned_worker:
            return ProjectMilestone.objects.none()

        return ProjectMilestone.objects.filter(
            project=project
        )

    def get_serializer_context(self):

        context = super().get_serializer_context()

        project = get_object_or_404(
            Project,
            id=self.kwargs["project_id"]
        )

        context["project"] = project

        return context

    def perform_create(self, serializer):

        project = get_object_or_404(
            Project,
            id=self.kwargs["project_id"]
        )

        if project.customer != self.request.user:
            raise PermissionDenied(
                "Only the project customer can create milestones."
            )

        serializer.save(
            project=project,
            created_by=self.request.user
        )


class ProjectMilestoneDetailView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = ProjectMilestoneSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):

        project = get_object_or_404(
            Project,
            id=self.kwargs["project_id"]
        )

        is_customer = project.customer == self.request.user

        is_assigned_worker = ProjectWorker.objects.filter(
            project=project,
            worker=self.request.user,
            status__in=[
                ProjectWorker.WorkerStatus.ACCEPTED,
                ProjectWorker.WorkerStatus.ACTIVE,
                ProjectWorker.WorkerStatus.COMPLETED,
            ]
        ).exists()

        if not is_customer and not is_assigned_worker:
            return ProjectMilestone.objects.none()

        return ProjectMilestone.objects.filter(
            project=project
        )

    def get_serializer_context(self):

        context = super().get_serializer_context()

        project = get_object_or_404(
            Project,
            id=self.kwargs["project_id"]
        )

        context["project"] = project

        return context

    def perform_update(self, serializer):

        project = get_object_or_404(
            Project,
            id=self.kwargs["project_id"]
        )

        if project.customer == self.request.user:
            serializer.save()
            return

        is_assigned_worker = ProjectWorker.objects.filter(
            project=project,
            worker=self.request.user,
            status__in=[
                ProjectWorker.WorkerStatus.ACCEPTED,
                ProjectWorker.WorkerStatus.ACTIVE,
            ]
        ).exists()

        if not is_assigned_worker:
            raise PermissionDenied(
                "Only the project customer or an active assigned "
                "worker can update project milestones."
            )

        serializer.save()


# ============================================================
# PROJECT PASSPORT
# ============================================================

class ProjectPassportView(generics.RetrieveAPIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = ProjectPassportSerializer

    def retrieve(self, request, *args, **kwargs):

        project = get_object_or_404(
            Project,
            id=kwargs["project_id"]
        )

        is_customer = project.customer == request.user

        is_assigned_worker = ProjectWorker.objects.filter(
            project=project,
            worker=request.user,
            status__in=[
                ProjectWorker.WorkerStatus.ACCEPTED,
                ProjectWorker.WorkerStatus.ACTIVE,
                ProjectWorker.WorkerStatus.COMPLETED,
            ]
        ).exists()

        if not is_customer and not is_assigned_worker:
            return Response(
                {
                    "detail": (
                        "You do not have permission to access "
                        "this project passport."
                    )
                },
                status=403
            )

        passport, created = ProjectPassport.objects.get_or_create(
            project=project,
            defaults={
                "passport_number": f"JW-{project.id:06d}"
            }
        )

        serializer = self.get_serializer(passport)

        return Response(serializer.data)


# ============================================================
# PROJECT ACTIVITIES
# ============================================================

class ProjectActivityListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = ProjectActivitySerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):

        project = get_object_or_404(
            Project,
            id=self.kwargs["project_id"]
        )

        is_customer = project.customer == self.request.user

        is_assigned_worker = ProjectWorker.objects.filter(
            project=project,
            worker=self.request.user,
            status__in=[
                ProjectWorker.WorkerStatus.ACCEPTED,
                ProjectWorker.WorkerStatus.ACTIVE,
                ProjectWorker.WorkerStatus.COMPLETED,
            ]
        ).exists()

        if not is_customer and not is_assigned_worker:
            return ProjectActivity.objects.none()

        return ProjectActivity.objects.filter(
            project=project
        )

    def get_serializer_context(self):

        context = super().get_serializer_context()

        project = get_object_or_404(
            Project,
            id=self.kwargs["project_id"]
        )

        context["project"] = project

        return context

    def perform_create(self, serializer):

        project = get_object_or_404(
            Project,
            id=self.kwargs["project_id"]
        )

        is_customer = project.customer == self.request.user

        is_assigned_worker = ProjectWorker.objects.filter(
            project=project,
            worker=self.request.user,
            status__in=[
                ProjectWorker.WorkerStatus.ACCEPTED,
                ProjectWorker.WorkerStatus.ACTIVE,
            ]
        ).exists()

        if not is_customer and not is_assigned_worker:
            raise PermissionDenied(
                "Only the project customer or an assigned worker "
                "can create project activities."
            )

        serializer.save(
            project=project,
            created_by=self.request.user
        )


# ============================================================
# MARKET LOCATIONS
# ============================================================

class MarketLocationListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = MarketLocationSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):
        return MarketLocation.objects.filter(
            is_active=True
        ).order_by(
            "county",
            "town",
            "name"
        )


class MarketLocationDetailView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = MarketLocationSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    queryset = MarketLocation.objects.all()


# ============================================================
# SUPPLIER PROFILE
# ============================================================

class SupplierProfileCreateView(
    generics.CreateAPIView
):

    serializer_class = SupplierProfileSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def perform_create(self, serializer):

        if SupplierProfile.objects.filter(
            user=self.request.user
        ).exists():

            raise ValidationError(
                "You already have a supplier profile."
            )

        serializer.save(
            user=self.request.user
        )


class SupplierProfileView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = SupplierProfileSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self):

        return get_object_or_404(
            SupplierProfile,
            user=self.request.user
        )


# ============================================================
# CONSTRUCTION MATERIALS
# ============================================================

class ConstructionMaterialListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = ConstructionMaterialSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):

        queryset = ConstructionMaterial.objects.filter(
            is_active=True
        ).order_by("category", "name")

        category = self.request.query_params.get(
            "category"
        )

        if category:
            queryset = queryset.filter(
                category__iexact=category
            )

        return queryset


class ConstructionMaterialDetailView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = ConstructionMaterialSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    queryset = ConstructionMaterial.objects.all()


# ============================================================
# MATERIAL PRICE OBSERVATIONS
# ============================================================

class MaterialPriceObservationListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = MaterialPriceObservationSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):

        queryset = MaterialPriceObservation.objects.select_related(
            "material",
            "supplier",
            "market"
        ).order_by(
            "-observed_on",
            "-created_at"
        )

        material_id = self.request.query_params.get(
            "material"
        )

        market_id = self.request.query_params.get(
            "market"
        )

        if material_id:
            queryset = queryset.filter(
                material_id=material_id
            )

        if market_id:
            queryset = queryset.filter(
                market_id=market_id
            )

        return queryset

    def perform_create(self, serializer):

        supplier = get_object_or_404(
            SupplierProfile,
            user=self.request.user
        )

        market = supplier.market

        serializer.save(
            supplier=supplier,
            submitted_by=self.request.user,
            source="SUPPLIER",
            market=market
        )


class MaterialPriceObservationDetailView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = MaterialPriceObservationSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):

        return MaterialPriceObservation.objects.filter(
            submitted_by=self.request.user
        )


# ============================================================
# LABOUR RATE OBSERVATIONS
# ============================================================

class LabourRateObservationListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = LabourRateObservationSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):

        queryset = LabourRateObservation.objects.select_related(
            "skill",
            "supplier",
            "market"
        ).order_by(
            "-observed_on",
            "-created_at"
        )

        skill_id = self.request.query_params.get(
            "skill"
        )

        market_id = self.request.query_params.get(
            "market"
        )

        if skill_id:
            queryset = queryset.filter(
                skill_id=skill_id
            )

        if market_id:
            queryset = queryset.filter(
                market_id=market_id
            )

        return queryset

    def perform_create(self, serializer):

        supplier = get_object_or_404(
            SupplierProfile,
            user=self.request.user
        )

        market = supplier.market

        serializer.save(
            supplier=supplier,
            submitted_by=self.request.user,
            source="SUPPLIER",
            market=market
        )


class LabourRateObservationDetailView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = LabourRateObservationSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):

        return LabourRateObservation.objects.filter(
            submitted_by=self.request.user
        )


# ============================================================
# COST ESTIMATES
# ============================================================

class CostEstimateListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = CostEstimateSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        HasCustomerRole,
    ]

    def get_queryset(self):

        return CostEstimate.objects.filter(
            project__customer=self.request.user
        ).order_by(
            "-created_at"
        )

    def perform_create(self, serializer):

        project = serializer.validated_data.get(
            "project"
        )

        if project.customer != self.request.user:
            raise PermissionDenied(
                "You can only create estimates for your own projects."
            )

        serializer.save(
            created_by=self.request.user
        )


class CostEstimateDetailView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = CostEstimateSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        HasCustomerRole,
    ]

    def get_queryset(self):

        return CostEstimate.objects.filter(
            project__customer=self.request.user
        )