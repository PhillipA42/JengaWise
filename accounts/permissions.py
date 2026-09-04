from rest_framework.permissions import BasePermission

from .models import Role


class HasCustomerRole(BasePermission):
    """
    Allows access only to users with the CUSTOMER role.
    """

    message = (
        "You must have the CUSTOMER role "
        "to access this resource."
    )

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.roles.filter(
                name=Role.RoleType.CUSTOMER
            ).exists()
        )


class HasWorkerRole(BasePermission):
    """
    Allows access only to users with the WORKER role.
    """

    message = (
        "You must have the WORKER role "
        "to access this resource."
    )

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.roles.filter(
                name=Role.RoleType.WORKER
            ).exists()
        )


class HasEquipmentOwnerRole(BasePermission):
    """
    Allows access only to users with the
    EQUIPMENT_OWNER role.
    """

    message = (
        "You must have the EQUIPMENT_OWNER role "
        "to access this resource."
    )

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.roles.filter(
                name=Role.RoleType.EQUIPMENT_OWNER
            ).exists()
        )