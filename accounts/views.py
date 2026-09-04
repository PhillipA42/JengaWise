from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import (
    CustomerProfile,
    EquipmentOwnerProfile,
    WorkerProfile,
    Skill,
) 

from .serializers import (
    CurrentUserSerializer,
    UserRegistrationSerializer,
    CustomerProfileSerializer,
    WorkerProfileSerializer,
    EquipmentOwnerProfileSerializer,
    SkillSerializer
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

        return Response(data)