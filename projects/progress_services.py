from django.db.models import Avg

from .models import ProjectMilestone


class ProjectProgressService:
    """
    Calculates the overall progress of a construction project
    based on its milestones.
    """

    @staticmethod
    def calculate_progress(project):

        result = ProjectMilestone.objects.filter(
            project=project
        ).aggregate(
            average_progress=Avg("progress_percentage")
        )

        average_progress = result["average_progress"]

        if average_progress is None:
            return 0

        return round(float(average_progress), 2)