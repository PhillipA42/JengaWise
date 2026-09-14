from django.db import models
from django.db.models import Sum

from .models import ProjectMilestone


class ProjectProgressService:

    @staticmethod
    def calculate_progress(project):

        result = ProjectMilestone.objects.filter(
            project=project
        ).aggregate(
            weighted_progress=Sum(
                models.F("progress_percentage")
                * models.F("weight")
            )
        )

        weighted_progress = result["weighted_progress"]

        if weighted_progress is None:
            return 0

        return round(
            float(weighted_progress) / 100,
            2
        )