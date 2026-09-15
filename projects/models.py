from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from accounts.models import Skill


class Project(models.Model):
    class ProjectStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        ON_HOLD = "ON_HOLD", "On Hold"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    name = models.CharField(max_length=200)

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )

    description = models.TextField(blank=True)

    project_type = models.CharField(max_length=100)

    location = models.CharField(max_length=200)

    address = models.CharField(
        max_length=255,
        blank=True,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    estimated_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    start_date = models.DateField(
        null=True,
        blank=True,
    )

    expected_completion_date = models.DateField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class ProjectRequiredSkill(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="required_skills",
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="project_requirements",
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "skill"],
                name="unique_project_required_skill",
            )
        ]

    def __str__(self):
        return f"{self.project.name} - {self.skill.name}"


class ProjectWorker(models.Model):
    class WorkerStatus(models.TextChoices):
        INVITED = "INVITED", "Invited"
        APPLIED = "APPLIED", "Applied"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        REMOVED = "REMOVED", "Removed"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="workers",
    )

    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_assignments",
    )

    status = models.CharField(
        max_length=20,
        choices=WorkerStatus.choices,
        default=WorkerStatus.INVITED,
    )

    invited_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "worker"],
                name="unique_project_worker",
            )
        ]

    def __str__(self):
        return f"{self.project.name} - {self.worker.username}"


class ProjectStatusHistory(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="status_history",
    )

    old_status = models.CharField(
        max_length=20,
        choices=Project.ProjectStatus.choices,
        null=True,
        blank=True,
    )

    new_status = models.CharField(
        max_length=20,
        choices=Project.ProjectStatus.choices,
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_status_changes",
    )

    reason = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.project.name}: "
            f"{self.old_status} → {self.new_status}"
        )


class ProjectMilestone(models.Model):
    class MilestoneStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        DELAYED = "DELAYED", "Delayed"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="milestones",
    )

    name = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    status = models.CharField(
        max_length=20,
        choices=MilestoneStatus.choices,
        default=MilestoneStatus.PENDING,
    )

    planned_start_date = models.DateField(
        null=True,
        blank=True,
    )

    planned_end_date = models.DateField(
        null=True,
        blank=True,
    )

    actual_completion_date = models.DateField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_milestones",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class ProjectPassport(models.Model):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="passport",
    )

    passport_number = models.CharField(
        max_length=50,
        unique=True,
    )

    issued_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.passport_number


class ProjectActivity(models.Model):
    class ActivityType(models.TextChoices):
        PROGRESS_UPDATE = "PROGRESS_UPDATE", "Progress Update"
        MILESTONE_UPDATE = "MILESTONE_UPDATE", "Milestone Update"
        MATERIAL_DELIVERY = "MATERIAL_DELIVERY", "Material Delivery"
        WORK_STARTED = "WORK_STARTED", "Work Started"
        WORK_COMPLETED = "WORK_COMPLETED", "Work Completed"
        ISSUE_REPORTED = "ISSUE_REPORTED", "Issue Reported"
        GENERAL_UPDATE = "GENERAL_UPDATE", "General Update"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="activities",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="project_activities",
    )

    activity_type = models.CharField(
        max_length=30,
        choices=ActivityType.choices,
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    milestone = models.ForeignKey(
        ProjectMilestone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )

    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.project.name} - {self.title}"


# ============================================================
# INTELLIGENT CONSTRUCTION COST ESTIMATION
# ============================================================


class MarketLocation(models.Model):
    """
    Represents a real construction-material market or geographic
    location from which price information can be associated.
    """

    country = models.CharField(
        max_length=100,
        default="Kenya",
    )

    county = models.CharField(
        max_length=100
    )

    town = models.CharField(
        max_length=100
    )

    area = models.CharField(
        max_length=150,
        blank=True,
    )

    name = models.CharField(
        max_length=200,
        help_text="Market or location name.",
    )

    address = models.CharField(
        max_length=255,
        blank=True,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "county",
            "town",
            "name",
        ]

    def __str__(self):
        location = f"{self.town}, {self.county}"
        return f"{self.name} - {location}"


class ConstructionMaterial(models.Model):
    """
    A material that can be priced and used in a construction estimate.
    """

    name = models.CharField(
        max_length=200
    )

    category = models.CharField(
        max_length=100,
        help_text="Example: Cement, Steel, Timber, Sand, Roofing.",
    )

    brand = models.CharField(
        max_length=100,
        blank=True,
    )

    specification = models.CharField(
        max_length=200,
        blank=True,
        help_text="Example: 50kg, 12mm, Grade 500.",
    )

    unit = models.CharField(
        max_length=50,
        help_text=(
            "Example: bag, kg, tonne, metre, piece, cubic metre."
        ),
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "category",
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "name",
                    "brand",
                    "specification",
                ],
                name="unique_construction_material_variant",
            )
        ]

    def __str__(self):
        details = " ".join(
            part
            for part in [
                self.name,
                self.brand,
                self.specification,
            ]
            if part
        )

        return f"{details} ({self.unit})"


class MaterialPriceObservation(models.Model):
    """
    A historical observation of a construction material price.

    Prices are NOT overwritten. Each observation becomes part of
    JengaWise's historical price intelligence.
    """

    class PriceSource(models.TextChoices):
        SUPPLIER = "SUPPLIER", "Registered Supplier"
        EXTERNAL = "EXTERNAL", "External Source"
        ADMIN = "ADMIN", "Administrator"

    material = models.ForeignKey(
        ConstructionMaterial,
        on_delete=models.CASCADE,
        related_name="price_observations",
    )

    supplier = models.ForeignKey(
        "accounts.SupplierProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="material_price_observations",
    )

    market = models.ForeignKey(
        MarketLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="material_price_observations",
    )

    price_per_unit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(0.01),
        ],
    )

    source = models.CharField(
        max_length=20,
        choices=PriceSource.choices,
    )

    source_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Supplier name, website, API or other source.",
    )

    source_url = models.URLField(
        blank=True
    )

    observed_on = models.DateField()

    is_verified = models.BooleanField(
        default=False
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_material_prices",
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            "-observed_on",
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "material",
                    "market",
                    "observed_on",
                ]
            ),
            models.Index(
                fields=[
                    "source",
                    "observed_on",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.material.name} - "
            f"KSh {self.price_per_unit} - "
            f"{self.observed_on}"
        )


class LabourRateObservation(models.Model):
    """
    Historical observation of labour rates.

    This allows JengaWise to learn labour prices by skill and location
    over time.
    """

    class RateSource(models.TextChoices):
        SUPPLIER = "SUPPLIER", "Registered Supplier"
        EXTERNAL = "EXTERNAL", "External Source"
        ADMIN = "ADMIN", "Administrator"

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="labour_rate_observations",
    )

    supplier = models.ForeignKey(
        "accounts.SupplierProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="labour_rate_observations",
    )

    market = models.ForeignKey(
        MarketLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="labour_rate_observations",
    )

    rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(0.01),
        ],
    )

    unit = models.CharField(
        max_length=50,
        default="day",
        help_text="Example: day, hour, job.",
    )

    source = models.CharField(
        max_length=20,
        choices=RateSource.choices,
    )

    source_name = models.CharField(
        max_length=255,
        blank=True,
    )

    source_url = models.URLField(
        blank=True
    )

    observed_on = models.DateField()

    is_verified = models.BooleanField(
        default=False
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_labour_rates",
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            "-observed_on",
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "skill",
                    "market",
                    "observed_on",
                ]
            ),
            models.Index(
                fields=[
                    "source",
                    "observed_on",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.skill.name} - "
            f"KSh {self.rate}/{self.unit} - "
            f"{self.observed_on}"
        )


class CostEstimate(models.Model):
    """
    A construction cost estimate generated for a project.

    The estimate stores a snapshot of the prices used so that a past
    quotation does not change when market prices change later.
    """

    class EstimateStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        GENERATED = "GENERATED", "Generated"
        APPROVED = "APPROVED", "Approved"
        EXPIRED = "EXPIRED", "Expired"

    class EstimationMethod(models.TextChoices):
        RULE_BASED = "RULE_BASED", "Rule Based"
        AI = "AI", "Artificial Intelligence"
        ML = "ML", "Machine Learning"
        MANUAL = "MANUAL", "Manual"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="cost_estimates",
    )

    name = models.CharField(
        max_length=200,
        default="Construction Cost Estimate",
    )

    pricing_market = models.ForeignKey(
        MarketLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cost_estimates",
    )

    price_as_of = models.DateField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=EstimateStatus.choices,
        default=EstimateStatus.DRAFT,
    )

    estimation_method = models.CharField(
        max_length=20,
        choices=EstimationMethod.choices,
        default=EstimationMethod.RULE_BASED,
    )

    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text="Confidence level from 0 to 100.",
    )

    material_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    labour_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    other_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    total_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    notes = models.TextField(
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_cost_estimates",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-created_at"
        ]

    def __str__(self):
        return f"{self.name} - {self.project.name}"


class EstimateMaterial(models.Model):
    """
    Material line item used in a specific estimate.

    The selected price observation is preserved for traceability.
    """

    estimate = models.ForeignKey(
        CostEstimate,
        on_delete=models.CASCADE,
        related_name="materials",
    )

    material = models.ForeignKey(
        ConstructionMaterial,
        on_delete=models.PROTECT,
        related_name="estimate_items",
    )

    price_observation = models.ForeignKey(
        MaterialPriceObservation,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="estimate_items",
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[
            MinValueValidator(0.001),
        ],
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
    )

    total_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.estimate.name} - {self.material.name}"


class EstimateLabour(models.Model):
    """
    Labour line item used in a specific estimate.

    The selected historical labour-rate observation is preserved.
    """

    estimate = models.ForeignKey(
        CostEstimate,
        on_delete=models.CASCADE,
        related_name="labour_items",
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.PROTECT,
        related_name="estimate_labour_items",
    )

    rate_observation = models.ForeignKey(
        LabourRateObservation,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="estimate_items",
    )

    workers_required = models.PositiveIntegerField(
        default=1
    )

    days_required = models.PositiveIntegerField(
        default=1
    )

    daily_rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
    )

    total_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.estimate.name} - {self.skill.name}"