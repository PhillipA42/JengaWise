from rest_framework import generics, permissions

from accounts.permissions import HasCustomerRole

from .models import WorkerReview
from .serializers import WorkerReviewSerializer


class WorkerReviewCreateView(
    generics.CreateAPIView
):

    serializer_class = WorkerReviewSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        HasCustomerRole,
    ]


class WorkerReviewListView(
    generics.ListAPIView
):

    serializer_class = WorkerReviewSerializer

    permission_classes = [
        permissions.AllowAny
    ]

    def get_queryset(self):

        worker_id = self.kwargs["worker_id"]

        return WorkerReview.objects.filter(
            worker_id=worker_id
        ).select_related(
            "customer",
            "worker__user",
            "project"
        )