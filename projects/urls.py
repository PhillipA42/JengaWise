from django.urls import path

from .views import (
    ProjectDetailView,
    ProjectHistoryView,
    ProjectListCreateView,
    ProjectWorkerMatchesView,
    InviteWorkerView,
    WorkerAssignmentStatusView,
)


urlpatterns = [

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
]