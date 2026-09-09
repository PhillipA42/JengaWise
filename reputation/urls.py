from django.urls import path

from .views import (
    WorkerReviewCreateView,
    WorkerReviewListView,
    WorkerReputationView,
)


urlpatterns = [

    # Create a worker review
    path(
        "reviews/",
        WorkerReviewCreateView.as_view(),
        name="worker-review-create",
    ),

    # Get all reviews for a worker
    path(
        "workers/<int:worker_id>/reviews/",
        WorkerReviewListView.as_view(),
        name="worker-review-list",
    ),

    path(
    "workers/<int:worker_id>/summary/",
    WorkerReputationView.as_view(),
    name="worker-reputation-summary",
    ),
]