from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import (
    CostEstimate,
    EstimateLabour,
    EstimateMaterial,
    LabourRateObservation,
    MaterialPriceObservation,
)


class ConstructionEstimationService:
    """
    Intelligent construction cost estimation service.

    Uses:
    - Project information
    - Required skills
    - Local market price observations
    - Local labour rate observations
    - Recent observations where available

    The service creates one CostEstimate together with
    material and labour breakdowns.
    """

    def __init__(
        self,
        project,
        pricing_market=None,
        created_by=None,
    ):
        self.project = project
        self.pricing_market = pricing_market
        self.created_by = created_by

    @transaction.atomic
    def generate_estimate(self, name=None):
        """
        Generate and save a complete construction estimate.
        """

        market = self.get_pricing_market()

        estimate = CostEstimate.objects.create(
            project=self.project,
            name=name or f"AI Estimate - {self.project.name}",
            pricing_market=market,
            price_as_of=timezone.now().date(),
            status=CostEstimate.EstimateStatus.GENERATED,
            estimation_method=CostEstimate.EstimationMethod.AI,
            created_by=self.created_by,
        )

        material_cost = self.generate_material_estimates(
            estimate,
            market,
        )

        labour_cost = self.generate_labour_estimates(
            estimate,
            market,
        )

        other_cost = self.calculate_other_cost(
            material_cost,
            labour_cost,
        )

        total_cost = (
            material_cost
            + labour_cost
            + other_cost
        )

        confidence_score = self.calculate_confidence_score(
            market=market,
            material_cost=material_cost,
            labour_cost=labour_cost,
        )

        estimate.material_cost = material_cost
        estimate.labour_cost = labour_cost
        estimate.other_cost = other_cost
        estimate.total_cost = total_cost
        estimate.confidence_score = confidence_score

        estimate.notes = self.generate_explanation(
            market=market,
            material_cost=material_cost,
            labour_cost=labour_cost,
            other_cost=other_cost,
            total_cost=total_cost,
            confidence_score=confidence_score,
        )

        estimate.save()

        return estimate

    def get_pricing_market(self):
        """
        Select the most appropriate market for the project.

        Priority:
        1. Explicitly supplied market
        2. Market matching project town
        3. Market matching project county
        4. Market matching project area
        5. First active market
        """

        if self.pricing_market:
            return self.pricing_market

        project_location = (
            self.project.location or ""
        ).strip().lower()

        if project_location:
            market = (
                self._market_queryset()
                .filter(town__iexact=project_location)
                .first()
            )

            if market:
                return market

            market = (
                self._market_queryset()
                .filter(county__iexact=project_location)
                .first()
            )

            if market:
                return market

            market = (
                self._market_queryset()
                .filter(area__iexact=project_location)
                .first()
            )

            if market:
                return market

        return self._market_queryset().first()

    def _market_queryset(self):
        from .models import MarketLocation

        return MarketLocation.objects.filter(
            is_active=True
        ).order_by(
            "ordering",
            "name",
        )

    def generate_material_estimates(
        self,
        estimate,
        market,
    ):
        """
        Generate material estimates from available
        local price observations.

        The most recent observation for each material
        is used.
        """

        if not market:
            return Decimal("0")

        observations = (
            MaterialPriceObservation.objects
            .filter(
                market=market,
                material__is_active=True,
            )
            .select_related("material")
            .order_by(
                "material_id",
                "-observed_on",
                "-created_at",
            )
        )

        total_material_cost = Decimal("0")
        processed_materials = set()

        for observation in observations:

            material = observation.material

            if material.id in processed_materials:
                continue

            processed_materials.add(material.id)

            unit_price = Decimal(
                observation.price_per_unit
            )

            quantity = self.estimate_material_quantity(
                material
            )

            total_cost = (
                quantity * unit_price
            ).quantize(
                Decimal("0.01")
            )

            EstimateMaterial.objects.create(
                estimate=estimate,
                material=material,
                price_observation=observation,
                quantity=quantity,
                unit_price=unit_price,
                total_cost=total_cost,
            )

            total_material_cost += total_cost

        return total_material_cost

    def estimate_material_quantity(self, material):
        """
        Estimate a prototype quantity.

        Detailed quantity take-off will later use:
        - project dimensions
        - project type
        - construction stage
        - AI/ML quantity prediction
        """

        category = (
            material.category or ""
        ).lower()

        name = (
            material.name or ""
        ).lower()

        text = f"{category} {name}"

        if "cement" in text:
            return Decimal("20")

        if "sand" in text:
            return Decimal("5")

        if "ballast" in text:
            return Decimal("5")

        if "steel" in text:
            return Decimal("10")

        if "brick" in text or "block" in text:
            return Decimal("500")

        if "timber" in text or "wood" in text:
            return Decimal("20")

        return Decimal("1")

    def generate_labour_estimates(
        self,
        estimate,
        market,
    ):
        """
        Generate labour estimates using the project's
        required skills and local labour rates.
        """

        if not market:
            return Decimal("0")

        total_labour_cost = Decimal("0")

        required_skills = (
            self.project.required_skills
            .select_related("skill")
            .order_by("priority")
        )

        for required_skill in required_skills:

            skill = required_skill.skill

            observation = (
                LabourRateObservation.objects
                .filter(
                    skill=skill,
                    market=market,
                )
                .order_by(
                    "-observed_on",
                    "-created_at",
                )
                .first()
            )

            if not observation:
                continue

            daily_rate = Decimal(
                observation.rate
            )

            workers_required = (
                self.estimate_workers_required(
                    required_skill.priority
                )
            )

            days_required = (
                self.estimate_days_required(
                    required_skill.priority
                )
            )

            total_cost = (
                daily_rate
                * workers_required
                * days_required
            ).quantize(
                Decimal("0.01")
            )

            EstimateLabour.objects.create(
                estimate=estimate,
                skill=skill,
                rate_observation=observation,
                workers_required=workers_required,
                days_required=days_required,
                daily_rate=daily_rate,
                total_cost=total_cost,
            )

            total_labour_cost += total_cost

        return total_labour_cost

    def estimate_workers_required(self, priority):
        """
        Estimate workers based on required skill priority.
        """

        if priority == 1:
            return 2

        if priority == 2:
            return 2

        return 1

    def estimate_days_required(self, priority):
        """
        Estimate working days based on required skill priority.
        """

        if priority == 1:
            return 10

        if priority == 2:
            return 7

        return 5

    def calculate_other_cost(
        self,
        material_cost,
        labour_cost,
    ):
        """
        Estimate transport, wastage, minor tools,
        and miscellaneous project costs.
        """

        subtotal = (
            material_cost
            + labour_cost
        )

        return (
            subtotal * Decimal("0.05")
        ).quantize(
            Decimal("0.01")
        )

    def calculate_confidence_score(
        self,
        market,
        material_cost,
        labour_cost,
    ):
        """
        Calculate an explainable confidence score.

        Confidence increases when:
        - A local market is available
        - Material pricing is available
        - Labour pricing is available
        - Required project skills are available
        """

        score = Decimal("30")

        if market:
            score += Decimal("20")

        if material_cost > 0:
            score += Decimal("20")

        if labour_cost > 0:
            score += Decimal("20")

        if self.project.required_skills.exists():
            score += Decimal("10")

        return min(
            int(score),
            100,
        )

    def generate_explanation(
        self,
        market,
        material_cost,
        labour_cost,
        other_cost,
        total_cost,
        confidence_score,
    ):
        """
        Generate a transparent explanation of the estimate.
        """

        market_name = (
            market.name
            if market
            else "available market data"
        )

        return (
            f"JengaWise generated this estimate using "
            f"construction pricing data associated with "
            f"{market_name}. "
            f"Estimated material cost is KSh "
            f"{material_cost:,.2f}, labour cost is KSh "
            f"{labour_cost:,.2f}, and other project costs "
            f"are KSh {other_cost:,.2f}. "
            f"The estimated total project cost is KSh "
            f"{total_cost:,.2f}. "
            f"The current confidence score is "
            f"{confidence_score}%. "
            f"Actual costs may vary depending on project "
            f"dimensions, material quantities, labour "
            f"requirements, supplier prices, and market "
            f"conditions."
        )