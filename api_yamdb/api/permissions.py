"""Application permission to only allow owners of an object to edit it."""

from rest_framework import permissions


class IsAuthorOrIsAuthenticated(permissions.BasePermission):
    message = 'Changing other people\'s content not allowed!'

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
