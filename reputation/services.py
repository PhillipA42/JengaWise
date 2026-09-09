from django.db.models import Avg

from .models import WorkerReview


class WorkerReputationService:
    """
    Calculates reputation statistics for workers
    based on customer reviews.
    """

    def __init__(self, worker):

        self.worker = worker

    def get_reputation(self):

        reviews = WorkerReview.objects.filter(
            worker=self.worker
        )

        total_reviews = reviews.count()

        if total_reviews == 0:

            return {
                "total_reviews": 0,
                "average_overall_rating": 0,
                "average_work_quality": 0,
                "average_professionalism": 0,
                "average_reliability": 0,
                "reputation_score": 0,
            }

        averages = reviews.aggregate(

            average_overall_rating=Avg(
                "overall_rating"
            ),

            average_work_quality=Avg(
                "work_quality"
            ),

            average_professionalism=Avg(
                "professionalism"
            ),

            average_reliability=Avg(
                "reliability"
            ),
        )

        weighted_rating = (

            averages["average_overall_rating"] * 0.40

            + averages["average_work_quality"] * 0.30

            + averages["average_professionalism"] * 0.15

            + averages["average_reliability"] * 0.15
        )

        reputation_score = (
            weighted_rating / 5
        ) * 100

        return {

            "total_reviews": total_reviews,

            "average_overall_rating": round(
                averages["average_overall_rating"],
                2
            ),

            "average_work_quality": round(
                averages["average_work_quality"],
                2
            ),

            "average_professionalism": round(
                averages["average_professionalism"],
                2
            ),

            "average_reliability": round(
                averages["average_reliability"],
                2
            ),

            "reputation_score": round(
                reputation_score,
                2
            ),
        }