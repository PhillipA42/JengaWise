from rest_framework import serializers

from accounts.models import Skill

from .models import (
    Project,
    ProjectRequiredSkill,
    ProjectWorker,
    ProjectStatusHistory,
    ProjectMilestone,
    ProjectPassport,
)


class ProjectRequiredSkillSerializer(serializers.ModelSerializer):
    """
    Displays a skill required by a project.
    """

    skill_name = serializers.CharField(
        source="skill.name",
        read_only=True
    )

    class Meta:
        model = ProjectRequiredSkill

        fields = (
            "id",
            "skill",
            "skill_name",
            "priority",
        )

        read_only_fields = (
            "id",
        )


class ProjectWorkerSerializer(serializers.ModelSerializer):

    worker_username = serializers.CharField(
        source="worker.username",
        read_only=True
    )

    worker_name = serializers.SerializerMethodField()

    project_name = serializers.CharField(
        source="project.name",
        read_only=True
    )

    class Meta:
        model = ProjectWorker

        fields = (
            "id",
            "project",
            "project_name",
            "worker",
            "worker_username",
            "worker_name",
            "status",
            "assigned_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "project_name",
            "worker_username",
            "worker_name",
            "assigned_at",
            "updated_at",
        )

    def get_worker_name(self, obj):

        return (
            f"{obj.worker.first_name} "
            f"{obj.worker.last_name}"
        ).strip()

class ProjectStatusHistorySerializer(serializers.ModelSerializer):
    """
    Displays the lifecycle history of a project.
    """

    changed_by_username = serializers.CharField(
        source="changed_by.username",
        read_only=True
    )

    class Meta:
        model = ProjectStatusHistory

        fields = (
            "id",
            "previous_status",
            "new_status",
            "changed_by",
            "changed_by_username",
            "notes",
            "changed_at",
        )

        read_only_fields = (
            "id",
            "changed_by",
            "changed_at",
        )


class ProjectSerializer(serializers.ModelSerializer):
    """
    Main serializer for creating, retrieving,
    and updating projects.
    """

    customer_username = serializers.CharField(
        source="customer.username",
        read_only=True
    )

    required_skills = ProjectRequiredSkillSerializer(
        many=True,
        read_only=True
    )

    project_workers = ProjectWorkerSerializer(
        many=True,
        read_only=True
    )

    status_history = ProjectStatusHistorySerializer(
        many=True,
        read_only=True
    )

    required_skill_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Skill.objects.all(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Project

        fields = (
            "id",
            "name",
            "customer",
            "customer_username",
            "description",
            "project_type",
            "location",
            "address",
            "latitude",
            "longitude",
            "estimated_budget",
            "start_date",
            "expected_completion_date",
            "status",
            "required_skills",
            "required_skill_ids",
            "project_workers",
            "status_history",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "customer",
            "customer_username",
            "required_skills",
            "project_workers",
            "status_history",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):

        required_skills = validated_data.pop(
            "required_skill_ids",
            []
        )

        project = Project.objects.create(
            **validated_data
        )

        for skill in required_skills:

            ProjectRequiredSkill.objects.create(
                project=project,
                skill=skill
            )

        return project

class WorkerMatchSerializer(serializers.Serializer):

    # Worker information
    worker_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    years_of_experience = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    # Worker statistics
    completed_jobs = serializers.SerializerMethodField()
    worker_reputation = serializers.SerializerMethodField()

    # Matching scores
    match_score = serializers.FloatField()
    skill_score = serializers.FloatField()
    experience_score = serializers.FloatField()
    location_score = serializers.FloatField()
    availability_score = serializers.FloatField()
    reputation_score = serializers.FloatField()
    completed_jobs_score = serializers.FloatField()

    def get_worker_id(self, obj):
        return obj["worker"].user.id

    def get_username(self, obj):
        return obj["worker"].user.username

    def get_first_name(self, obj):
        return obj["worker"].user.first_name

    def get_last_name(self, obj):
        return obj["worker"].user.last_name

    def get_profile_image(self, obj):

        worker = obj["worker"]

        if worker.profile_image:
            return worker.profile_image.url

        return None

    def get_years_of_experience(self, obj):
        return obj["worker"].years_of_experience

    def get_location(self, obj):
        return obj["worker"].location

    def get_skills(self, obj):

        return [
            skill.name
            for skill in obj["worker"].skills.all()
        ]

    def get_completed_jobs(self, obj):

        return obj["worker"].completed_jobs

    def get_worker_reputation(self, obj):

        from reputation.services import (
            WorkerReputationService
        )

        reputation_service = WorkerReputationService(
            obj["worker"]
        )

        reputation = reputation_service.get_reputation()

        return reputation["reputation_score"]


class ProjectMilestoneSerializer(serializers.ModelSerializer):

    project_name = serializers.CharField(
        source="project.name",
        read_only=True
    )

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True
    )

    class Meta:
        model = ProjectMilestone

        fields = (
            "id",
            "project",
            "project_name",
            "name",
            "description",
            "progress_percentage",
            "status",
            "start_date",
            "expected_completion_date",
            "actual_completion_date",
            "notes",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "project",
            "project_name",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):

        progress = attrs.get(
            "progress_percentage",
            self.instance.progress_percentage
            if self.instance
            else 0
        )

        status = attrs.get(
            "status",
            self.instance.status
            if self.instance
            else ProjectMilestone.MilestoneStatus.NOT_STARTED
        )

        if progress == 100:
            status = ProjectMilestone.MilestoneStatus.COMPLETED
            attrs["status"] = status

        if (
            progress < 100
            and status == ProjectMilestone.MilestoneStatus.COMPLETED
        ):
            raise serializers.ValidationError(
                "A milestone can only be marked completed "
                "when progress is 100%."
            )

        return attrs

class ProjectPassportSerializer(serializers.ModelSerializer):

    project_name = serializers.CharField(
        source="project.name",
        read_only=True
    )

    project_status = serializers.CharField(
        source="project.status",
        read_only=True
    )

    customer_username = serializers.CharField(
        source="project.customer.username",
        read_only=True
    )

    overall_progress = serializers.SerializerMethodField()

    class Meta:
        model = ProjectPassport

        fields = (
            "id",
            "project",
            "project_name",
            "customer_username",
            "passport_number",
            "project_status",
            "overall_progress",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "project",
            "project_name",
            "customer_username",
            "passport_number",
            "project_status",
            "overall_progress",
            "created_at",
            "updated_at",
        )

    def get_overall_progress(self, obj):

        from .progress_services import ProjectProgressService

        return ProjectProgressService.calculate_progress(
            obj.project
        )