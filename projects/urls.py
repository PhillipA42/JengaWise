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

    path(
    "<int:project_id>/complete/",
    CompleteProjectView.as_view(),
    name="complete-project"
    ),

    path(
    "<int:project_id>/milestones/",

    ProjectMilestoneListCreateView.as_view(),
    name="project-milestones"
    ),

    path(
    "<int:project_id>/milestones/<int:pk>/",
    ProjectMilestoneDetailView.as_view(),
    name="project-milestone-detail"
    ),

    path(
    "<int:project_id>/passport/",
    ProjectPassportView.as_view(),
    name="project-passport"
    ),

    path(
    "<int:project_id>/activities/",
    ProjectActivityListCreateView.as_view(),
    name="project-activities"
),
]