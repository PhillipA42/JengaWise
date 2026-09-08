from rest_framework import serializers

from accounts.models import Skill

from .models import (
    Project,
    ProjectRequiredSkill,
    ProjectWorker,
    ProjectStatusHistory,
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
    """
    Displays a worker associated with a project.
    """

    worker_username = serializers.CharField(
        source="worker.username",
        read_only=True
    )

    worker_name = serializers.SerializerMethodField()

    class Meta:
        model = ProjectWorker

        fields = (
            "id",
            "worker",
            "worker_username",
            "worker_name",
            "status",
            "assigned_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
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

    worker_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    years_of_experience = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    match_score = serializers.FloatField()
    skill_score = serializers.FloatField()
    experience_score = serializers.FloatField()
    location_score = serializers.FloatField()
    availability_score = serializers.FloatField()

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