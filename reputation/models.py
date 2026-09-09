from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from projects.models import Project


class WorkerReview(models.Model):
    """
    Customer review and rating of a worker for a project.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="worker_reviews"
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="worker_reviews_given"
    )

    worker = models.ForeignKey(
        "accounts.WorkerProfile",
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    overall_rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )

    work_quality = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )

    professionalism = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )

    reliability = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )

    comment = models.TextField(
        blank=True
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

        constraints = [

            # A customer can review a particular worker
            # only once for the same project.
            models.UniqueConstraint(
                fields=[
                    "project",
                    "customer",
                    "worker",
                ],
                name="unique_worker_review_per_project"
            )
        ]

    def __str__(self):

        return (
            f"{self.customer.username} → "
            f"{self.worker.user.username} "
            f"({self.overall_rating}/5)"
        )