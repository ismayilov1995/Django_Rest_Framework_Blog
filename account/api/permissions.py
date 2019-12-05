from rest_framework.permissions import BasePermission


class IsAnonymous(BasePermission):
    message = "You must be logout saw this page"

    def has_permission(self, request, view):
        return not request.user.is_authenticated
