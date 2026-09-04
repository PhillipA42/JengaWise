from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """
    Represents a role that can be assigned to a JengaWise user.
    """

    class RoleType(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        CUSTOMER = "CUSTOMER", "Customer"
        WORKER = "WORKER", "Construction Worker"
        EQUIPMENT_OWNER = "EQUIPMENT_OWNER", "Equipment Owner"

    name = models.CharField(
        max_length=30,
        choices=RoleType.choices,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.get_name_display()

class User(AbstractUser):
    """
    Custom user model for the JengaWise platform.
    """

    email = models.EmailField(
        unique=True
    )

    phone_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    roles = models.ManyToManyField(
        Role,
        related_name="users",
        blank=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.email

class Skill(models.Model):
    """
    Represents a professional skill that can be assigned
    to construction workers.
    """

    name = models.CharField(
        max_length=100,
        unique=True
    )

    category = models.CharField(
        max_length=100,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class CustomerProfile(models.Model):
    """
    Additional profile information for customers.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile"
    )

    profile_image = models.ImageField(
        upload_to="profiles/customers/",
        null=True,
        blank=True
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    bio = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} - Customer"


class WorkerProfile(models.Model):
    """
    Professional profile for construction workers.
    """

    class AvailabilityStatus(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        BUSY = "BUSY", "Busy"
        UNAVAILABLE = "UNAVAILABLE", "Unavailable"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="worker_profile"
    )

    profile_image = models.ImageField(
        upload_to="profiles/workers/",
        null=True,
        blank=True
    )

    bio = models.TextField(
        blank=True
    )

    years_of_experience = models.PositiveIntegerField(
        default=0
    )

    skills = models.ManyToManyField(
        Skill,
        related_name="workers",
        blank=True
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    availability_status = models.CharField(
        max_length=20,
        choices=AvailabilityStatus.choices,
        default=AvailabilityStatus.AVAILABLE
    )

    is_verified = models.BooleanField(
        default=False
    )

    completed_jobs = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} - Worker"


class EquipmentOwnerProfile(models.Model):
    """
    Profile for users who own construction equipment
    and want to rent it through JengaWise.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="equipment_owner_profile"
    )

    profile_image = models.ImageField(
        upload_to="profiles/equipment_owners/",
        null=True,
        blank=True
    )

    business_name = models.CharField(
        max_length=255,
        blank=True
    )

    business_description = models.TextField(
        blank=True
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        if self.business_name:
            return self.business_name

        return f"{self.user.username} - Equipment Owner"