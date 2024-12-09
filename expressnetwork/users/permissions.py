from rest_framework.permissions import BasePermission
from generics.permissions import is_user_allowed
from users.models import Role


class UsersPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list','retrieve','options']:
            return bool(
                is_user_allowed(request,Role.RoleName.superadmin) or\
                is_user_allowed(request,Role.RoleName.admin) or\
                is_user_allowed(request,Role.RoleName.technician)
            )            
        elif view.action in ['create', 'partial_update', 'destroy']:
            return bool(
                is_user_allowed(request,Role.RoleName.superadmin) or\
                is_user_allowed(request,Role.RoleName.admin)
            )
        elif view.action in ['update']:
            return bool(
                is_user_allowed(request,Role.RoleName.superadmin) or\
                is_user_allowed(request,Role.RoleName.admin) 
            )
        else:
            return False


class OrganizationPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['create', 'update', 'partial_update', 'destroy','list']:
            return bool(
                is_user_allowed(request,Role.RoleName.superadmin)
            )
        elif view.action in ['retrieve']:
            return bool(
                is_user_allowed(request,Role.RoleName.admin) or\
                is_user_allowed(request,Role.RoleName.superadmin)
            )            
        else:
            return False


class UserActivityPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return bool(
                is_user_allowed(request,Role.RoleName.superadmin) or\
                is_user_allowed(request,Role.RoleName.admin) or\
                is_user_allowed(request,Role.RoleName.technician) or\
                is_user_allowed(request,Role.RoleName.user)
            )
        elif request.method in ['POST','PUT','DELETE']:
            return bool(
                is_user_allowed(request,Role.RoleName.superadmin) or\
                is_user_allowed(request,Role.RoleName.admin)
            )
        else:
            return False