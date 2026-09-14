from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Project, ProjectWorker, ProjectStatusHistory


class ProjectCompletionService:
    """
    Handles project completion and completion validation.
    """

    @staticmethod
    @transaction.atomic
    def complete_project(project, customer, notes=""):

        # Only the project owner can complete the project.
        if project.customer != customer:
            raise ValidationError(
                "Only the project customer can complete this project."
            )

        # Project must currently be in progress.
        if project.status != Project.ProjectStatus.IN_PROGRESS:
            raise ValidationError(
                "Only projects that are in progress can be completed."
            )

        # Get all workers assigned to this project.
        assignments = ProjectWorker.objects.filter(
            project=project
        )

        # A project should have at least one worker assignment
        # before it can be completed.
        if not assignments.exists():
            raise ValidationError(
                "A project must have at least one assigned worker "
                "before it can be completed."
            )

        # Check whether any assigned worker has not completed
        # their assignment.
        incomplete_assignments = assignments.exclude(
            status=ProjectWorker.WorkerStatus.COMPLETED
        )

        if incomplete_assignments.exists():
            raise ValidationError(
                "All assigned workers must complete their assignments "
                "before the project can be completed."
            )

        previous_status = project.status

        project.status = Project.ProjectStatus.COMPLETED

        project.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # Record the project status change.
        ProjectStatusHistory.objects.create(
            project=project,
            previous_status=previous_status,
            new_status=Project.ProjectStatus.COMPLETED,
            changed_by=customer,
            notes=notes,
        )

        return project