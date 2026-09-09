
from django.db import transaction
from rest_framework.exceptions import ValidationError

from accounts.models import WorkerProfile

from .models import Project, ProjectWorker


class ProjectHiringService:
    """
    Handles worker invitations and workforce lifecycle.
    """

    @staticmethod
    @transaction.atomic
    def invite_worker(project, worker, customer):

        if project.customer != customer:
            raise ValidationError(
                "You can only invite workers to your own projects."
            )

        if project.status not in [
            Project.ProjectStatus.OPEN,
            Project.ProjectStatus.IN_PROGRESS,
        ]:
            raise ValidationError(
                "Workers can only be invited to open or active projects."
            )

        if not worker.roles.filter(name="WORKER").exists():
            raise ValidationError(
                "The selected user is not registered as a worker."
            )

        assignment, created = (
            ProjectWorker.objects.get_or_create(
                project=project,
                worker=worker,
                defaults={
                    "status": ProjectWorker.WorkerStatus.INVITED
                }
            )
        )

        if not created:

            if assignment.status in [
                ProjectWorker.WorkerStatus.ACCEPTED,
                ProjectWorker.WorkerStatus.ACTIVE,
                ProjectWorker.WorkerStatus.COMPLETED,
            ]:
                raise ValidationError(
                    "This worker already has an active or completed "
                    "assignment on this project."
                )

            assignment.status = ProjectWorker.WorkerStatus.INVITED

            assignment.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return assignment

    @staticmethod
    @transaction.atomic
    def update_worker_status(
        assignment,
        new_status,
        user
    ):

        project = assignment.project

        current_status = assignment.status

        allowed_transitions = {

            ProjectWorker.WorkerStatus.INVITED: [
                ProjectWorker.WorkerStatus.ACCEPTED,
                ProjectWorker.WorkerStatus.REJECTED,
            ],

            ProjectWorker.WorkerStatus.ACCEPTED: [
                ProjectWorker.WorkerStatus.ACTIVE,
                ProjectWorker.WorkerStatus.REMOVED,
            ],

            ProjectWorker.WorkerStatus.ACTIVE: [
                ProjectWorker.WorkerStatus.COMPLETED,
                ProjectWorker.WorkerStatus.REMOVED,
            ],

            ProjectWorker.WorkerStatus.REJECTED: [],

            ProjectWorker.WorkerStatus.COMPLETED: [],

            ProjectWorker.WorkerStatus.REMOVED: [],

            ProjectWorker.WorkerStatus.APPLIED: [
                ProjectWorker.WorkerStatus.ACCEPTED,
                ProjectWorker.WorkerStatus.REJECTED,
            ],
        }

        if new_status not in allowed_transitions.get(
            current_status,
            []
        ):
            raise ValidationError(
                f"Cannot change worker status from "
                f"{current_status} to {new_status}."
            )

        # Worker can accept/reject their own invitation.
        if new_status in [
            ProjectWorker.WorkerStatus.ACCEPTED,
            ProjectWorker.WorkerStatus.REJECTED,
        ]:

            if assignment.worker != user:
                raise ValidationError(
                    "Only the invited worker can accept "
                    "or reject this invitation."
                )

        # Customer controls activation/removal.
        if new_status in [
            ProjectWorker.WorkerStatus.ACTIVE,
            ProjectWorker.WorkerStatus.REMOVED,
        ]:

            if project.customer != user:
                raise ValidationError(
                    "Only the project customer can "
                    "activate or remove a worker."
                )

        # Worker marks their own work as completed.
        if new_status == ProjectWorker.WorkerStatus.COMPLETED:

            if assignment.worker != user:
                raise ValidationError(
                    "Only the assigned worker can "
                    "mark their work as completed."
                )

        assignment.status = new_status

        assignment.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # Automatically update the worker's completed jobs.
        # This happens only when an active assignment becomes completed.
        if new_status == ProjectWorker.WorkerStatus.COMPLETED:

            worker_profile = WorkerProfile.objects.get(
                user=assignment.worker
            )

            worker_profile.completed_jobs += 1

            worker_profile.save(
                update_fields=[
                    "completed_jobs"
                ]
            )

        return assignment