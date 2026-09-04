from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    Role,
    Skill,
    CustomerProfile,
    WorkerProfile,
    EquipmentOwnerProfile,
)


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Handles registration of new JengaWise users.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    password_confirm = serializers.CharField(
        write_only=True
    )

    roles = serializers.ListField(
        child=serializers.ChoiceField(
            choices=Role.RoleType.choices
        ),
        write_only=True,
        required=True,
        min_length=1
    )

    class Meta:
        model = User

        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password",
            "password_confirm",
            "roles",
        )

        read_only_fields = (
            "id",
        )

    def validate_roles(self, roles):

        if Role.RoleType.ADMIN in roles:
            raise serializers.ValidationError(
                "You cannot register yourself as an administrator."
            )

        return roles

    def validate(self, attrs):
        """
        Validate password confirmation.
        """

        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {
                    "password_confirm":
                        "Passwords do not match."
                }
            )

        return attrs

    def create(self, validated_data):

        roles_data = validated_data.pop(
            "roles",
            []
        )

        validated_data.pop(
            "password_confirm"
        )

        password = validated_data.pop(
            "password"
        )

        user = User(
            **validated_data
        )

        user.set_password(password)

        user.save()

        for role_name in roles_data:

            role, created = Role.objects.get_or_create(
                name=role_name
            )

            user.roles.add(role)

            if role_name == Role.RoleType.CUSTOMER:
                CustomerProfile.objects.get_or_create(
                    user=user
                )

            elif role_name == Role.RoleType.WORKER:
                WorkerProfile.objects.get_or_create(
                    user=user
                )

            elif role_name == Role.RoleType.EQUIPMENT_OWNER:
                EquipmentOwnerProfile.objects.get_or_create(
                    user=user
                )

        return user

class CurrentUserSerializer(serializers.ModelSerializer):

    roles = serializers.SerializerMethodField()

    class Meta:

        model = User

        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "roles",
            "is_verified",
            "created_at",
        )

        read_only_fields = fields

    def get_roles(self, obj):

        return [
            role.name
            for role in obj.roles.all()
        ]

class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer for construction and professional skills.
    """

    class Meta:
        model = Skill
        fields = (
            "id",
            "name",
            "category",
            "description",
        )


class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for customer profile information.
    """

    user = CurrentUserSerializer(
        read_only=True
    )

    class Meta:
        model = CustomerProfile

        fields = (
            "id",
            "user",
            "profile_image",
            "location",
            "address",
            "bio",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
        )


class WorkerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for construction worker profiles.
    """

    user = CurrentUserSerializer(
        read_only=True
    )

    skills = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Skill.objects.all(),
        required=False
    )

    skill_details = SkillSerializer(
        source="skills",
        many=True,
        read_only=True
    )

    class Meta:
        model = WorkerProfile

        fields = (
            "id",
            "user",
            "profile_image",
            "bio",
            "years_of_experience",
            "skills",
            "skill_details",
            "location",
            "latitude",
            "longitude",
            "availability_status",
            "is_verified",
            "completed_jobs",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "user",
            "is_verified",
            "completed_jobs",
            "created_at",
            "updated_at",
        )


class EquipmentOwnerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for equipment owner profiles.
    """

    user = CurrentUserSerializer(
        read_only=True
    )

    class Meta:
        model = EquipmentOwnerProfile

        fields = (
            "id",
            "user",
            "profile_image",
            "business_name",
            "business_description",
            "location",
            "address",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
        )