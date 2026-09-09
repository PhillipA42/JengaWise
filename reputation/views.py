from rest_framework import generics, permissions

from accounts.permissions import HasCustomerRole

from .models import WorkerReview
from .serializers import WorkerReviewSerializer

from accounts.models import WorkerProfile

from .services import WorkerReputationService
from rest_framework.response import Response


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

class WorkerReputationView(
    generics.GenericAPIView
):

    permission_classes = [
        permissions.AllowAny
    ]

    def get(self, request, worker_id):

        try:

            worker = WorkerProfile.objects.get(
                id=worker_id
            )

        except WorkerProfile.DoesNotExist:

            from rest_framework.exceptions import NotFound

            raise NotFound(
                "Worker profile not found."
            )

        reputation_service = (
            WorkerReputationService(worker)
        )

        reputation = (
            reputation_service.get_reputation()
        )

        return Response(
            {
                "worker_id": worker.id,

                "worker_username": (
                    worker.user.username
                ),

                **reputation,
            }
        )