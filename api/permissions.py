from rest_framework import permissions
from filesharing.models import Directory


class UserPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return obj.has_access(request.user)
        elif request.method == 'POST':
            return obj.parent.has_access(request.user)
        else:
            return obj.has_access(request.user) and obj not in Directory.objects.root_nodes()
