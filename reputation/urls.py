from django.urls import path

from .views import (
    WorkerReviewCreateView,
    WorkerReviewListView,
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
]