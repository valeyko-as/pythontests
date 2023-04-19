from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        user = view.kwargs.get('pk')
        return str(request.user.id) == str(user)
