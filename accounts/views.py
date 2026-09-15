from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import (
    CustomerProfile,
    EquipmentOwnerProfile,
    WorkerProfile,
    SupplierProfile,
    Skill,
)

from .serializers import (
    CurrentUserSerializer,
    UserRegistrationSerializer,
    CustomerProfileSerializer,
    WorkerProfileSerializer,
    EquipmentOwnerProfileSerializer,
    SupplierProfileSerializer,
    SkillSerializer,
)

from .permissions import (
    HasCustomerRole,
    HasWorkerRole,
    HasEquipmentOwnerRole,
)


class RegisterView(generics.CreateAPIView):

    serializer_class = UserRegistrationSerializer

    permission_classes = [
        permissions.AllowAny
    ]


class CurrentUserView(generics.GenericAPIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = CurrentUserSerializer

    def get(self, request):

        serializer = self.get_serializer(
            request.user
        )

        return Response(
            serializer.data
        )


class CustomerProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = CustomerProfileSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        HasCustomerRole,
    ]

    def get_object(self):

        profile, created = CustomerProfile.objects.get_or_create(
            user=self.request.user
        )

        return profile


class WorkerProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = WorkerProfileSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        HasWorkerRole,
    ]

    def get_object(self):

        profile, created = WorkerProfile.objects.get_or_create(
            user=self.request.user
        )

        return profile


class EquipmentOwnerProfileView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = EquipmentOwnerProfileSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        HasEquipmentOwnerRole,
    ]

    def get_object(self):

        profile, created = (
            EquipmentOwnerProfile.objects.get_or_create(
                user=self.request.user
            )
        )

        return profile


class SupplierProfileCreateView(generics.CreateAPIView):

    serializer_class = SupplierProfileSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def perform_create(self, serializer):

        if SupplierProfile.objects.filter(
            user=self.request.user
        ).exists():

            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                "You already have a supplier profile."
            )

        serializer.save(
            user=self.request.user
        )


class SupplierProfileView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = SupplierProfileSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self):

        from django.shortcuts import get_object_or_404

        return get_object_or_404(
            SupplierProfile,
            user=self.request.user
        )


class SkillListView(generics.ListAPIView):

    queryset = Skill.objects.all().order_by(
        "name"
    )

    serializer_class = SkillSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]


class MyProfilesView(generics.GenericAPIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request):

        user = request.user

        data = {
            "user": CurrentUserSerializer(user).data,
            "customer_profile": None,
            "worker_profile": None,
            "equipment_owner_profile": None,
            "supplier_profile": None,
        }

        if hasattr(user, "customer_profile"):

            data["customer_profile"] = (
                CustomerProfileSerializer(
                    user.customer_profile
                ).data
            )

        if hasattr(user, "worker_profile"):

            data["worker_profile"] = (
                WorkerProfileSerializer(
                    user.worker_profile
                ).data
            )

        if hasattr(user, "equipment_owner_profile"):

            data["equipment_owner_profile"] = (
                EquipmentOwnerProfileSerializer(
                    user.equipment_owner_profile
                ).data
            )

        if hasattr(user, "supplier_profile"):

            data["supplier_profile"] = (
                SupplierProfileSerializer(
                    user.supplier_profile
                ).data
            )

        return Response(data)