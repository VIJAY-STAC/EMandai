from rest_framework import permissions

class IsFarmer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_farmer


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_customer