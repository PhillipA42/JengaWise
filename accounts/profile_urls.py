from django.urls import path

from .views import (
    MyProfilesView,
    CustomerProfileView,
    WorkerProfileView,
    EquipmentOwnerProfileView,
    SkillListView,
)


urlpatterns = [

    path(
        "me/",
        MyProfilesView.as_view(),
        name="my-profiles",
    ),

    path(
        "customer/",
        CustomerProfileView.as_view(),
        name="customer-profile",
    ),

    path(
        "worker/",
        WorkerProfileView.as_view(),
        name="worker-profile",
    ),

    path(
        "equipment-owner/",
        EquipmentOwnerProfileView.as_view(),
        name="equipment-owner-profile",
    ),

    path(
        "skills/",
        SkillListView.as_view(),
        name="skill-list",
    ),
]