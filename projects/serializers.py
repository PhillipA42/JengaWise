from django.utils import timezone
from rest_framework import serializers

from accounts.models import Skill

from .models import (
    Project,
    ProjectRequiredSkill,
    ProjectWorker,
    ProjectStatusHistory,
    ProjectMilestone,
    ProjectPassport,
    ProjectActivity,
    MarketLocation,
    ConstructionMaterial,
    MaterialPriceObservation,
    LabourRateObservation,
    CostEstimate,
    EstimateMaterial,
    EstimateLabour,
)


# ============================================================
# PROJECT REQUIRED SKILL
# ============================================================

class ProjectRequiredSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(
        source="skill.name",
        read_only=True,
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
            "skill_name",
        )


# ============================================================
# PROJECT WORKER
# ============================================================

class ProjectWorkerSerializer(serializers.ModelSerializer):
    worker_username = serializers.CharField(
        source="worker.username",
        read_only=True,
    )

    worker_name = serializers.SerializerMethodField()

    project_name = serializers.CharField(
        source="project.name",
        read_only=True,
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
            "invited_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "project_name",
            "worker_username",
            "worker_name",
            "invited_at",
            "updated_at",
        )

    def get_worker_name(self, obj):
        return (
            f"{obj.worker.first_name} "
            f"{obj.worker.last_name}"
        ).strip() or obj.worker.username


# ============================================================
# PROJECT STATUS HISTORY
# ============================================================

class ProjectStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_username = serializers.CharField(
        source="changed_by.username",
        read_only=True,
    )

    class Meta:
        model = ProjectStatusHistory

        fields = (
            "id",
            "project",
            "old_status",
            "new_status",
            "changed_by",
            "changed_by_username",
            "reason",
            "created_at",
        )

        read_only_fields = (
            "id",
            "project",
            "old_status",
            "new_status",
            "changed_by",
            "changed_by_username",
            "created_at",
        )


# ============================================================
# PROJECT
# ============================================================

class ProjectSerializer(serializers.ModelSerializer):
    customer_username = serializers.CharField(
        source="customer.username",
        read_only=True,
    )

    required_skills = ProjectRequiredSkillSerializer(
        many=True,
        read_only=True,
    )

    project_workers = ProjectWorkerSerializer(
        source="workers",
        many=True,
        read_only=True,
    )

    status_history = ProjectStatusHistorySerializer(
        many=True,
        read_only=True,
    )

    required_skill_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Skill.objects.all(),
        write_only=True,
        required=False,
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
            [],
        )

        project = Project.objects.create(
            **validated_data
        )

        for skill in required_skills:
            ProjectRequiredSkill.objects.create(
                project=project,
                skill=skill,
            )

        return project


# ============================================================
# WORKER MATCHING
# ============================================================

class WorkerMatchSerializer(serializers.Serializer):
    worker_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    years_of_experience = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    completed_jobs = serializers.SerializerMethodField()
    worker_reputation = serializers.SerializerMethodField()

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
        from reputation.services import WorkerReputationService

        reputation_service = WorkerReputationService(
            obj["worker"]
        )

        reputation = reputation_service.get_reputation()

        return reputation["reputation_score"]


# ============================================================
# PROJECT MILESTONE
# ============================================================

class ProjectMilestoneSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source="project.name",
        read_only=True,
    )

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = ProjectMilestone

        fields = (
            "id",
            "project",
            "project_name",
            "name",
            "description",
            "weight",
            "progress_percentage",
            "status",
            "planned_start_date",
            "planned_end_date",
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
            else 0,
        )

        weight = attrs.get(
            "weight",
            self.instance.weight
            if self.instance
            else 0,
        )

        requested_status = attrs.get(
            "status",
            self.instance.status
            if self.instance
            else ProjectMilestone.MilestoneStatus.PENDING,
        )

        # ----------------------------------------------------
        # Automatically determine status from progress
        # ----------------------------------------------------

        if progress == 100:
            attrs["status"] = (
                ProjectMilestone.MilestoneStatus.COMPLETED
            )

            if (
                not self.instance
                or not self.instance.actual_completion_date
            ):
                attrs["actual_completion_date"] = (
                    timezone.localdate()
                )

        else:
            if requested_status == (
                ProjectMilestone.MilestoneStatus.COMPLETED
            ):
                raise serializers.ValidationError({
                    "status": (
                        "A milestone can only be marked completed "
                        "when progress is 100%."
                    )
                })

            if (
                self.instance
                and self.instance.status
                == ProjectMilestone.MilestoneStatus.COMPLETED
            ):
                attrs["status"] = (
                    ProjectMilestone.MilestoneStatus.IN_PROGRESS
                )

            attrs["actual_completion_date"] = None

        # ----------------------------------------------------
        # Validate total milestone weight
        # ----------------------------------------------------

        project = (
            self.instance.project
            if self.instance
            else self.context.get("project")
        )

        if project:
            existing_milestones = ProjectMilestone.objects.filter(
                project=project
            )

            if self.instance:
                existing_milestones = (
                    existing_milestones.exclude(
                        id=self.instance.id
                    )
                )

            existing_weight = sum(
                milestone.weight
                for milestone in existing_milestones
            )

            total_weight = existing_weight + weight

            if total_weight > 100:
                raise serializers.ValidationError({
                    "weight": (
                        "The total weight of all project "
                        "milestones cannot exceed 100%."
                    )
                })

        return attrs


# ============================================================
# PROJECT PASSPORT
# ============================================================

class ProjectPassportSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source="project.name",
        read_only=True,
    )

    project_status = serializers.CharField(
        source="project.status",
        read_only=True,
    )

    customer_username = serializers.CharField(
        source="project.customer.username",
        read_only=True,
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
            "issued_at",
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
            "issued_at",
            "updated_at",
        )

    def get_overall_progress(self, obj):
        from .progress_services import ProjectProgressService

        return ProjectProgressService.calculate_progress(
            obj.project
        )


# ============================================================
# PROJECT ACTIVITY
# ============================================================

class ProjectActivitySerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source="project.name",
        read_only=True,
    )

    milestone_name = serializers.CharField(
        source="milestone.name",
        read_only=True,
    )

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = ProjectActivity

        fields = (
            "id",
            "project",
            "project_name",
            "milestone",
            "milestone_name",
            "activity_type",
            "title",
            "description",
            "progress_percentage",
            "created_by",
            "created_by_username",
            "created_at",
        )

        read_only_fields = (
            "id",
            "project",
            "project_name",
            "milestone_name",
            "created_by",
            "created_by_username",
            "created_at",
        )

    def validate(self, attrs):
        milestone = attrs.get("milestone")

        if milestone:
            project = self.context.get("project")

            if project and milestone.project != project:
                raise serializers.ValidationError({
                    "milestone": (
                        "The selected milestone does not belong "
                        "to this project."
                    )
                })

        progress = attrs.get("progress_percentage")

        if progress is not None and not 0 <= progress <= 100:
            raise serializers.ValidationError({
                "progress_percentage": (
                    "Progress must be between 0 and 100."
                )
            })

        return attrs


# ============================================================
# MARKET LOCATION
# ============================================================

class MarketLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketLocation

        fields = (
            "id",
            "country",
            "county",
            "town",
            "area",
            "name",
            "address",
            "latitude",
            "longitude",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


# ============================================================
# CONSTRUCTION MATERIAL
# ============================================================

class ConstructionMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructionMaterial

        fields = (
            "id",
            "name",
            "category",
            "brand",
            "specification",
            "unit",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


# ============================================================
# MATERIAL PRICE OBSERVATION
# ============================================================

class MaterialPriceObservationSerializer(
    serializers.ModelSerializer
):
    material_name = serializers.CharField(
        source="material.name",
        read_only=True,
    )

    supplier_name = serializers.CharField(
        source="supplier.business_name",
        read_only=True,
    )

    market_name = serializers.CharField(
        source="market.name",
        read_only=True,
    )

    submitted_by_username = serializers.CharField(
        source="submitted_by.username",
        read_only=True,
    )

    class Meta:
        model = MaterialPriceObservation

        fields = (
            "id",
            "material",
            "material_name",
            "supplier",
            "supplier_name",
            "market",
            "market_name",
            "price_per_unit",
            "source",
            "source_name",
            "source_url",
            "observed_on",
            "is_verified",
            "submitted_by",
            "submitted_by_username",
            "notes",
            "created_at",
        )

        read_only_fields = (
            "id",
            "material_name",
            "supplier_name",
            "market_name",
            "submitted_by",
            "submitted_by_username",
            "is_verified",
            "created_at",
        )

    def validate(self, attrs):
        source = attrs.get(
            "source",
            self.instance.source
            if self.instance
            else None,
        )

        supplier = attrs.get(
            "supplier",
            self.instance.supplier
            if self.instance
            else None,
        )

        if (
            source == MaterialPriceObservation.PriceSource.SUPPLIER
            and not supplier
        ):
            raise serializers.ValidationError({
                "supplier": (
                    "A registered supplier is required "
                    "for supplier price observations."
                )
            })

        return attrs


# ============================================================
# LABOUR RATE OBSERVATION
# ============================================================

class LabourRateObservationSerializer(
    serializers.ModelSerializer
):
    skill_name = serializers.CharField(
        source="skill.name",
        read_only=True,
    )

    supplier_name = serializers.CharField(
        source="supplier.business_name",
        read_only=True,
    )

    market_name = serializers.CharField(
        source="market.name",
        read_only=True,
    )

    submitted_by_username = serializers.CharField(
        source="submitted_by.username",
        read_only=True,
    )

    class Meta:
        model = LabourRateObservation

        fields = (
            "id",
            "skill",
            "skill_name",
            "supplier",
            "supplier_name",
            "market",
            "market_name",
            "rate",
            "unit",
            "source",
            "source_name",
            "source_url",
            "observed_on",
            "is_verified",
            "submitted_by",
            "submitted_by_username",
            "notes",
            "created_at",
        )

        read_only_fields = (
            "id",
            "skill_name",
            "supplier_name",
            "market_name",
            "submitted_by",
            "submitted_by_username",
            "is_verified",
            "created_at",
        )

    def validate(self, attrs):
        source = attrs.get(
            "source",
            self.instance.source
            if self.instance
            else None,
        )

        supplier = attrs.get(
            "supplier",
            self.instance.supplier
            if self.instance
            else None,
        )

        if (
            source == LabourRateObservation.RateSource.SUPPLIER
            and not supplier
        ):
            raise serializers.ValidationError({
                "supplier": (
                    "A registered supplier is required "
                    "for supplier labour-rate observations."
                )
            })

        return attrs


# ============================================================
# COST ESTIMATE
# ============================================================

class CostEstimateSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source="project.name",
        read_only=True,
    )

    pricing_market_name = serializers.CharField(
        source="pricing_market.name",
        read_only=True,
    )

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = CostEstimate

        fields = (
            "id",
            "project",
            "project_name",
            "name",
            "pricing_market",
            "pricing_market_name",
            "price_as_of",
            "status",
            "estimation_method",
            "confidence_score",
            "material_cost",
            "labour_cost",
            "other_cost",
            "total_cost",
            "notes",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "project_name",
            "pricing_market_name",
            "material_cost",
            "labour_cost",
            "total_cost",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        )


# ============================================================
# ESTIMATE MATERIAL
# ============================================================

class EstimateMaterialSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(
        source="material.name",
        read_only=True,
    )

    observation_date = serializers.DateField(
        source="price_observation.observed_on",
        read_only=True,
    )

    class Meta:
        model = EstimateMaterial

        fields = (
            "id",
            "estimate",
            "material",
            "material_name",
            "price_observation",
            "observation_date",
            "quantity",
            "unit_price",
            "total_cost",
            "created_at",
        )

        read_only_fields = (
            "id",
            "material_name",
            "observation_date",
            "total_cost",
            "created_at",
        )

    def validate(self, attrs):
        quantity = attrs.get("quantity")

        if quantity is not None and quantity <= 0:
            raise serializers.ValidationError({
                "quantity": (
                    "Quantity must be greater than zero."
                )
            })

        return attrs


# ============================================================
# ESTIMATE LABOUR
# ============================================================

class EstimateLabourSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(
        source="skill.name",
        read_only=True,
    )

    observation_date = serializers.DateField(
        source="rate_observation.observed_on",
        read_only=True,
    )

    class Meta:
        model = EstimateLabour

        fields = (
            "id",
            "estimate",
            "skill",
            "skill_name",
            "rate_observation",
            "observation_date",
            "workers_required",
            "days_required",
            "daily_rate",
            "total_cost",
            "created_at",
        )

        read_only_fields = (
            "id",
            "skill_name",
            "observation_date",
            "total_cost",
            "created_at",
        )

    def validate(self, attrs):
        workers_required = attrs.get(
            "workers_required"
        )

        days_required = attrs.get(
            "days_required"
        )

        if (
            workers_required is not None
            and workers_required <= 0
        ):
            raise serializers.ValidationError({
                "workers_required": (
                    "Workers required must be greater than zero."
                )
            })

        if (
            days_required is not None
            and days_required <= 0
        ):
            raise serializers.ValidationError({
                "days_required": (
                    "Days required must be greater than zero."
                )
            })

        return attrs