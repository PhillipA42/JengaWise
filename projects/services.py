from accounts.models import WorkerProfile

from .models import Project


class WorkerMatchingService:
    """
    Matches construction workers to projects based on
    skills, experience, location, and availability.
    """

    def __init__(self, project):

        self.project = project

    def get_matches(self):

        workers = WorkerProfile.objects.select_related(
            "user"
        ).prefetch_related(
            "skills"
        )

        matches = []

        for worker in workers:

            score_data = self.calculate_match_score(
                worker
            )

            if score_data["match_score"] > 0:

                matches.append(
                    {
                        "worker": worker,
                        **score_data,
                    }
                )

        matches.sort(
            key=lambda match: match["match_score"],
            reverse=True
        )

        return matches

    def calculate_match_score(self, worker):

        skill_score = self.calculate_skill_score(
            worker
        )

        experience_score = (
            self.calculate_experience_score(
                worker
            )
        )

        location_score = self.calculate_location_score(
            worker
        )

        availability_score = (
            self.calculate_availability_score(
                worker
            )
        )

        total_score = (
            skill_score
            + experience_score
            + location_score
            + availability_score
        )

        return {
            "match_score": round(total_score, 2),
            "skill_score": round(skill_score, 2),
            "experience_score": round(
                experience_score,
                2
            ),
            "location_score": round(
                location_score,
                2
            ),
            "availability_score": round(
                availability_score,
                2
            ),
        }

    def calculate_skill_score(self, worker):

        required_skills = set(
            self.project.required_skills.values_list(
                "skill_id",
                flat=True
            )
        )

        worker_skills = set(
            worker.skills.values_list(
                "id",
                flat=True
            )
        )

        if not required_skills:

            return 40

        matched_skills = (
            required_skills.intersection(
                worker_skills
            )
        )

        match_percentage = (
            len(matched_skills)
            / len(required_skills)
        )

        return match_percentage * 40

    def calculate_experience_score(self, worker):

        years = worker.years_of_experience

        if years >= 10:

            return 20

        return (years / 10) * 20

    def calculate_location_score(self, worker):

        if not worker.location or not self.project.location:

            return 0

        project_location = (
            self.project.location.lower().strip()
        )

        worker_location = (
            worker.location.lower().strip()
        )

        # Exact location match
        if project_location == worker_location:

            return 20

        # Partial location match
        if (
            project_location in worker_location
            or worker_location in project_location
        ):

            return 15

        return 0
    def calculate_availability_score(self, worker):

        if (
            worker.availability_status
            == WorkerProfile.AvailabilityStatus.AVAILABLE
        ):

            return 20

        return 0