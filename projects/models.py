from django.conf import settings
from django.db import models

from accounts.models import Skill


class Project(models.Model):
    """
    Represents a construction or skilled-work project
    created by a customer.
    """

    class ProjectType(models.TextChoices):
        RESIDENTIAL = "RESIDENTIAL", "Residential Construction"
        COMMERCIAL = "COMMERCIAL", "Commercial Construction"
        RENOVATION = "RENOVATION", "Renovation"
        REPAIR = "REPAIR", "Repair and Maintenance"
        PLUMBING = "PLUMBING", "Plumbing"
        ELECTRICAL = "ELECTRICAL", "Electrical Installation"
        PAINTING = "PAINTING", "Painting"
        ROOFING = "ROOFING", "Roofing"
        OTHER = "OTHER", "Other"

    class ProjectStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        ON_HOLD = "ON_HOLD", "On Hold"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    name = models.CharField(
        max_length=255
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects"
    )

    description = models.TextField()

    project_type = models.CharField(
        max_length=30,
        choices=ProjectType.choices
    )

    location = models.CharField(
        max_length=255
    )

    address = models.TextField(
        blank=True
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    estimated_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )

    start_date = models.DateField(
        null=True,
        blank=True
    )

    expected_completion_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT
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
    """
    Represents a professional skill required
    for a particular project.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="required_skills"
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="required_for_projects"
    )

    priority = models.PositiveSmallIntegerField(
        default=1
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "project",
                    "skill"
                ],
                name="unique_project_required_skill"
            )
        ]

    def __str__(self):
        return (
            f"{self.project.name} - "
            f"{self.skill.name}"
        )


class ProjectWorker(models.Model):
    """
    Represents a worker associated with
    a specific project.
    """

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
        related_name="project_workers"
    )

    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_assignments"
    )

    status = models.CharField(
        max_length=20,
        choices=WorkerStatus.choices,
        default=WorkerStatus.INVITED
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "project",
                    "worker"
                ],
                name="unique_project_worker"
            )
        ]

    def __str__(self):
        return (
            f"{self.worker.username} - "
            f"{self.project.name}"
        )


class ProjectStatusHistory(models.Model):
    """
    Stores the history of important
    project status changes.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="status_history"
    )

    previous_status = models.CharField(
        max_length=20,
        choices=Project.ProjectStatus.choices,
        null=True,
        blank=True
    )

    new_status = models.CharField(
        max_length=20,
        choices=Project.ProjectStatus.choices
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="project_status_changes"
    )

    notes = models.TextField(
        blank=True
    )

    changed_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            "-changed_at"
        ]

    def __str__(self):
        return (
            f"{self.project.name}: "
            f"{self.previous_status} → "
            f"{self.new_status}"
        )