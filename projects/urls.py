from django.urls import path

from .views import (
    ProjectDetailView,
    ProjectHistoryView,
    ProjectListCreateView,
    ProjectMilestoneListCreateView,
    ProjectWorkerMatchesView,
    InviteWorkerView,
    WorkerAssignmentStatusView,
    CompleteProjectView,
    ProjectMilestoneDetailView,
    ProjectPassportView,
    ProjectActivityListCreateView,
    MarketLocationListCreateView,
    MarketLocationDetailView,
    ConstructionMaterialListCreateView,
    ConstructionMaterialDetailView,
    MaterialPriceObservationListCreateView,
    MaterialPriceObservationDetailView,
    LabourRateObservationListCreateView,
    LabourRateObservationDetailView,
    CostEstimateListCreateView,
    CostEstimateDetailView,
)


urlpatterns = [

    # ========================================================
    # PROJECTS
    # ========================================================

    path(
        "",
        ProjectListCreateView.as_view(),
        name="project-list-create",
    ),

    path(
        "<int:project_id>/history/",
        ProjectHistoryView.as_view(),
        name="project-history",
    ),

    path(
        "<int:project_id>/matches/",
        ProjectWorkerMatchesView.as_view(),
        name="project-worker-matches",
    ),

    path(
        "<int:pk>/",
        ProjectDetailView.as_view(),
        name="project-detail",
    ),

    # ========================================================
    # PROJECT WORKERS
    # ========================================================

    path(
        "<int:project_id>/workers/invite/",
        InviteWorkerView.as_view(),
        name="invite-worker",
    ),

    path(
        "workers/<int:assignment_id>/status/",
        WorkerAssignmentStatusView.as_view(),
        name="worker-assignment-status",
    ),

    # ========================================================
    # PROJECT COMPLETION
    # ========================================================

    path(
        "<int:project_id>/complete/",
        CompleteProjectView.as_view(),
        name="complete-project",
    ),

    # ========================================================
    # PROJECT MILESTONES
    # ========================================================

    path(
        "<int:project_id>/milestones/",
        ProjectMilestoneListCreateView.as_view(),
        name="project-milestones",
    ),

    path(
        "<int:project_id>/milestones/<int:pk>/",
        ProjectMilestoneDetailView.as_view(),
        name="project-milestone-detail",
    ),

    # ========================================================
    # PROJECT PASSPORT
    # ========================================================

    path(
        "<int:project_id>/passport/",
        ProjectPassportView.as_view(),
        name="project-passport",
    ),

    # ========================================================
    # PROJECT ACTIVITIES
    # ========================================================

    path(
        "<int:project_id>/activities/",
        ProjectActivityListCreateView.as_view(),
        name="project-activities",
    ),

    # ========================================================
    # MARKET LOCATIONS
    # ========================================================

    path(
        "markets/",
        MarketLocationListCreateView.as_view(),
        name="market-list-create",
    ),

    path(
        "markets/<int:pk>/",
        MarketLocationDetailView.as_view(),
        name="market-detail",
    ),

    # ========================================================
    # CONSTRUCTION MATERIALS
    # ========================================================

    path(
        "materials/",
        ConstructionMaterialListCreateView.as_view(),
        name="material-list-create",
    ),

    path(
        "materials/<int:pk>/",
        ConstructionMaterialDetailView.as_view(),
        name="material-detail",
    ),

    # ========================================================
    # MATERIAL PRICE OBSERVATIONS
    # ========================================================

    path(
        "material-prices/",
        MaterialPriceObservationListCreateView.as_view(),
        name="material-price-list-create",
    ),

    path(
        "material-prices/<int:pk>/",
        MaterialPriceObservationDetailView.as_view(),
        name="material-price-detail",
    ),

    # ========================================================
    # LABOUR RATE OBSERVATIONS
    # ========================================================

    path(
        "labour-rates/",
        LabourRateObservationListCreateView.as_view(),
        name="labour-rate-list-create",
    ),

    path(
        "labour-rates/<int:pk>/",
        LabourRateObservationDetailView.as_view(),
        name="labour-rate-detail",
    ),

    # ========================================================
    # COST ESTIMATES
    # ========================================================

    path(
        "estimates/",
        CostEstimateListCreateView.as_view(),
        name="cost-estimate-list-create",
    ),

    path(
        "estimates/<int:pk>/",
        CostEstimateDetailView.as_view(),
        name="cost-estimate-detail",
    ),
]