from rest_framework import serializers

from accounts.models import WorkerProfile
from projects.models import Project

from .models import WorkerReview


class WorkerReviewSerializer(serializers.ModelSerializer):

    customer_username = serializers.CharField(
        source="customer.username",
        read_only=True
    )

    worker_username = serializers.CharField(
        source="worker.user.username",
        read_only=True
    )

    class Meta:

        model = WorkerReview

        fields = (
            "id",
            "project",
            "customer",
            "customer_username",
            "worker",
            "worker_username",
            "overall_rating",
            "work_quality",
            "professionalism",
            "reliability",
            "comment",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "customer",
            "customer_username",
            "worker_username",
            "created_at",
            "updated_at",
        )

    def validate_project(self, project):

        request = self.context["request"]

        if project.customer != request.user:

            raise serializers.ValidationError(
                "You can only review workers for your own projects."
            )

        return project

    def validate(self, attrs):

        request = self.context["request"]

        project = attrs.get("project")
        worker = attrs.get("worker")

        # Ensure the project belongs to the customer
        if project.customer != request.user:

            raise serializers.ValidationError(
                {
                    "project":
                    "You can only review workers for your own projects."
                }
            )

        # Prevent a worker from being reviewed twice
        # by the same customer on the same project.
        if WorkerReview.objects.filter(
            project=project,
            customer=request.user,
            worker=worker
        ).exists():

            raise serializers.ValidationError(
                "You have already reviewed this worker for this project."
            )

        return attrs

    def create(self, validated_data):

        request = self.context["request"]

        return WorkerReview.objects.create(
            customer=request.user,
            **validated_data
        )