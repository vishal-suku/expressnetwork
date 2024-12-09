from django.shortcuts import render

import datetime

from drf_spectacular.utils import extend_schema,OpenApiParameter
from django.db.models import Q

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework_simplejwt import serializers as jwt_serializers
from rest_framework_simplejwt.views import TokenViewBase


from users.permissions import UsersPermission, OrganizationPermission
from users import utils
from users import serializers, models, configurations, permissions
from generics import paginations
from django.utils import timezone
# Create your views here.

# For test users
class UserView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, UsersPermission]
    serializer_class = serializers.UserInfoModelSerializer
    queryset = models.User.objects.none()

    def get_queryset(self):
        if models.Role.objects.get(user=self.request.user).role == models.Role.RoleName.superadmin:
            return models.User.objects.filter(is_active=True).order_by('username')

        organization = models.Role.objects.filter(user=self.request.user).select_related("organization").first()
        organization = models.Role.objects.filter(organization=organization.organization).select_related("user")
        user_list = [i.user for i in organization if i.is_active]
        return models.User.objects.filter(username__in=user_list).order_by('username')

    
    @extend_schema(
        tags=['users'],
        request=None,
        parameters=[
            OpenApiParameter(name='page_number', required=False, type=int, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='data_per_page', required=False, type=int, location=OpenApiParameter.QUERY),
        ],
        responses={200: serializers.UserInfoModelSerializer})
    def list(self, request):
        """
        Lists all Users
        """
        page_number = request.query_params.get('page_number', 1)
        data_per_page = request.query_params.get('data_per_page', 10)
        queryset = self.get_queryset()
        serializer = serializers.UserInfoModelSerializer
        pagination = paginations.Pagination()
        serialized_data, pages = pagination.get_paginated_response(
            queryset=queryset,page_number=page_number,data_per_page=data_per_page,serializer_class=serializer
        )
        data = {
            "details": {
                "data": serialized_data,
                "pagination": {
                    "current_page": page_number,
                    "total_pages": pages,
                    "page_range": list(range(1, int(pages) + 1)),
                }
            }
        }
        return Response(data=data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['users'],
        request=None,
        responses={200: dict})
    @action(detail=False)
    def options(self, request):
        """Necessary data for user creation"""
        role = models.Role.objects.get(user=request.user).role
        if role in ['superadmin','Super Admin']:
            result = {"roles": [{"id": choice, "name": value} for choice, value in models.Role.RoleName.choices]}
        elif role in ['admin','Organization Admin']:
            result = {"roles":[{"id": choice, "name": value} for choice, value in models.Role.RoleName.choices if choice.lower() != 'superadmin']}
        else:
            excluded_roles = ['superadmin', 'admin', 'organization admin']
            result = {"roles":[{"id": choice, "name": value} for choice, value in models.Role.RoleName.choices if choice.lower() not in excluded_roles]}

        return Response(data=result, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['users'],
        request=serializers.CreateUserSerializer,
        responses={200: dict, 400: dict, 403: dict, 409: dict})
    def create(self, request):
        """Creating users for organizations
         - API allowed by super admins or organizational admins only
         - If an organizational admin try to create a user in another organization,
            - Returns 403
        """
        serializer = serializers.CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        first_name: str = serializer.validated_data.get('first_name', None)
        last_name: str = serializer.validated_data.get('last_name', None)
        email: str = serializer.validated_data.get('email', None)
        phone: str = serializer.validated_data.get('phone', None)
        role: str = serializer.validated_data.get('role', None)
        org_id: str = serializer.validated_data.get('organization', None)
        try:
            current_role = models.Role.objects.get(user=request.user)
        except models.Role.DoesNotExist:
            Response(data={"detail": "You do not have permission to access this."}, status=status.HTTP_403_FORBIDDEN)

        if not ((current_role.role == models.Role.RoleName.superadmin) or (current_role.role == models.Role.RoleName.admin)):
            Response(data={"detail": "You do not have permission to access this."}, status=status.HTTP_403_FORBIDDEN)

        if (org_id == None) and (current_role.role == models.Role.RoleName.admin):
            Response(data={"detail": "You do not have permission to access this."}, status=status.HTTP_403_FORBIDDEN)

        if current_role.role == models.Role.RoleName.superadmin:
            organization = models.Organization.objects.filter(id=org_id).first()

        elif current_role.role == models.Role.RoleName.admin:
            organization = current_role.organization
          
        else:
            Response(data={"detail": "You do not have permission to access this."}, status=status.HTTP_403_FORBIDDEN)

        utils.create_user(first_name, last_name, organization, email.lower(), phone, role, request_user=request.user)
        sites_functions.create_activity_log(
        user=request.user, 
        activity= {
            "message" : f"Created User <strong>{first_name} {last_name}</strong>",
            "activity": "Created user", 
            "old_value": first_name, 
            "new_value": first_name
        }
        )
        user = models.User.objects.filter(username=email.lower()).first()
        role_value = ''
        if role == models.Role.RoleName.superadmin :
            role_value = "Super Admin"
        elif role == models.Role.RoleName.admin:
            role_value = "Organization Admin"
        elif role == models.Role.RoleName.manager:
            role_value = "Manager"
        else:
            role_value = "User"
        return Response(data={'detail': f'{role_value} created successfully', 'id': user.id}, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['users'],
        request=serializers.UpdateOrganizationUserSerializer,
        responses={200: dict, 400: dict, 403: dict, 409: dict})
    def update(self, request, pk):
        """Updating a user_id
         - if SuperAdmin:
            - Update role, org, fname, lname, phone
         - else if OrganizationAdmin:
            - Cannot modify other organization's users
            - Update role, fname, lname, phone
         - else:
            - Cannot modify other users
            - Cannot modify own role
            - Update fname, lname, phone
        """
        serializer = serializers.UpdateOrganizationUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role: str = serializer.validated_data.get('role', None)
        first_name: str = serializer.validated_data.get('first_name', None)
        last_name: str = serializer.validated_data.get('last_name', None)
        phone: str = serializer.validated_data.get('phone', None)

        loggined_user=request.user
        current = utils.get_current_org_role(request.user.id)
        requested = utils.get_current_org_role(pk)

        try:
            user = models.User.objects.get(id=pk,is_active=True)
        except:
            return Response(data={"detail": "Requested user does not exists"}, status=status.HTTP_404_NOT_FOUND)
        
        if role == models.Role.RoleName.superadmin:
            if current.role != models.Role.RoleName.superadmin:
                return Response(data={"detail": "You do not have the permission to modify role to Super Admin"}, status=status.HTTP_403_FORBIDDEN)
            if requested.organization:
                return Response(data={"detail": "Only enterprise users can be Super Admin"}, status=status.HTTP_403_FORBIDDEN)                

        if current.role == models.Role.RoleName.superadmin:
            utils.update_user_detail(user, first_name, last_name, phone, loggined_user)
            utils.update_user_role(user, role, loggined_user)
            return Response(data={"detail": "User details has been updated."}, status=status.HTTP_200_OK)
        
        elif current.role == models.Role.RoleName.admin:
            if requested.organization is None:
                return Response(data={"detail": "You do not have the permission to modify enterprise users"}, status=status.HTTP_403_FORBIDDEN)
            if str(requested.organization.id) != str(current.organization.id):
                return Response(data={"detail": "User does not belong to your organization"}, status=status.HTTP_400_BAD_REQUEST)
            
            utils.update_user_detail(user, first_name, last_name, phone, loggined_user)
            utils.update_user_role(user, role, loggined_user)
            return Response(data={"detail": "User details has been updated."}, status=status.HTTP_200_OK)

        else:
            try:
                if int(pk) != int(request.user.id):
                    return Response(data={"detail": "You do not have permission to modify another users"}, status=status.HTTP_403_FORBIDDEN)            
                if current.role != role:
                    return Response(data={"detail": "You do not have permission to change your role"}, status=status.HTTP_403_FORBIDDEN)
            except:
                return Response(data={"detail": "You do not have permission to modify another users"}, status=status.HTTP_403_FORBIDDEN)
            utils.update_user_detail(user, first_name, last_name, phone, loggined_user)
            return Response(data={"detail": "User details has been updated."}, status=status.HTTP_200_OK)
    
    @extend_schema(tags=['users'],responses = {202: dict,400: dict, 403: dict, 404: dict})
    def destroy(self, request, pk):
        if int(pk)==int(request.user.id): return Response(data={"detail": "Permission Denied. This Action Cannot be Performed"}, status=status.HTTP_403_FORBIDDEN)
        requested = utils.get_current_org_role(pk)
        current = utils.get_current_org_role(request.user.id)
        if (current.role == models.Role.RoleName.admin) and (requested.organization != current.organization):
            return Response(data={"detail": "User does not belong to your organization"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.get_queryset().get(pk=pk)
        except models.User.DoesNotExist:
            return Response(data={"detail": f"{pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        user = utils.delete_user(pk,request.user)
        fullname = user.first_name+' '+user.last_name
        sites_functions.create_activity_log(
            user=request.user, 
            activity= {
                "activity": "Deleted user", 
                "message":f"Deleted user <strong>{fullname}</strong>",
                "old_value": user.first_name, 
                "new_value": user.first_name
            }
        )
        return Response(data={"status": "User deleted successfully"}, status=status.HTTP_202_ACCEPTED)


# For Hub CRUD Operations
class OrganizationView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, OrganizationPermission]
    serializer_class = serializers.HubInfoModelSerializer
    queryset = models.User.objects.none()

    def get_queryset(self):
        if models.Role.objects.get(user=self.request.user).role == models.Role.RoleName.superadmin:
            return models.User.objects.filter(is_active=True).order_by('username')

        organization = models.Role.objects.filter(user=self.request.user).select_related("organization").first()
        organization = models.Role.objects.filter(organization=organization.organization).select_related("user")
        user_list = [i.user for i in organization if i.is_active]
        return models.User.objects.filter(username__in=user_list).order_by('username')

    
    @extend_schema(
        tags=['users'],
        request=None,
        parameters=[
            OpenApiParameter(name='page_number', required=False, type=int, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='data_per_page', required=False, type=int, location=OpenApiParameter.QUERY),
        ],
        responses={200: serializers.UserInfoModelSerializer})
    def list(self, request):
        """
        Lists all Users
        """
        page_number = request.query_params.get('page_number', 1)
        data_per_page = request.query_params.get('data_per_page', 10)
        queryset = self.get_queryset()
        serializer = serializers.UserInfoModelSerializer
        pagination = paginations.Pagination()
        serialized_data, pages = pagination.get_paginated_response(
            queryset=queryset,page_number=page_number,data_per_page=data_per_page,serializer_class=serializer
        )
        data = {
            "details": {
                "data": serialized_data,
                "pagination": {
                    "current_page": page_number,
                    "total_pages": pages,
                    "page_range": list(range(1, int(pages) + 1)),
                }
            }
        }
        return Response(data=data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['users'],
        request=None,
        responses={200: dict})
    @action(detail=False)
    def options(self, request):
        """Necessary data for user creation"""
        role = models.Role.objects.get(user=request.user).role
        if role in ['superadmin','Super Admin']:
            result = {"roles": [{"id": choice, "name": value} for choice, value in models.Role.RoleName.choices]}
        elif role in ['admin','Organization Admin']:
            result = {"roles":[{"id": choice, "name": value} for choice, value in models.Role.RoleName.choices if choice.lower() != 'superadmin']}
        else:
            excluded_roles = ['superadmin', 'admin', 'organization admin']
            result = {"roles":[{"id": choice, "name": value} for choice, value in models.Role.RoleName.choices if choice.lower() not in excluded_roles]}

        return Response(data=result, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['users'],
        request=serializers.HubInfoModelSerializer,
        responses={200: dict, 400: dict, 403: dict, 409: dict})
    def create(self, request):
        """Creating users for organizations/hubs
         - API allowed by super admins only
         - If an organizational admin try to create a user in another organization,
            - Returns 403
        """
        print("Inside create...")
        serializer = serializers.HubInfoModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name: str = serializer.validated_data.get('name', None)
        email: str = serializer.validated_data.get('email', None)
        phone: str = serializer.validated_data.get('phone', None)
        location: str = serializer.validated_data.get('location', None)
        try:
            current_role = models.Role.objects.get(user=request.user)
        except models.Role.DoesNotExist:
            Response(data={"detail": "You do not have permission to access this."}, status=status.HTTP_403_FORBIDDEN)

        if current_role.role == models.Role.RoleName.superadmin:
            id_value = utils.create_hub(name, email.lower(), phone, location, current_role.role, request_user=request.user)
        else:
            Response(data={"detail": "You do not have permission to access this."}, status=status.HTTP_403_FORBIDDEN)
        return Response(data={'detail': f'{name} hub created successfully', 'id': id_value}, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['users'],
        request=serializers.UpdateOrganizationUserSerializer,
        responses={200: dict, 400: dict, 403: dict, 409: dict})
    def update(self, request, pk):
        """Updating a user_id
         - if SuperAdmin:
            - Update role, org, fname, lname, phone
         - else if OrganizationAdmin:
            - Cannot modify other organization's users
            - Update role, fname, lname, phone
         - else:
            - Cannot modify other users
            - Cannot modify own role
            - Update fname, lname, phone
        """
        serializer = serializers.UpdateOrganizationUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role: str = serializer.validated_data.get('role', None)
        first_name: str = serializer.validated_data.get('first_name', None)
        last_name: str = serializer.validated_data.get('last_name', None)
        phone: str = serializer.validated_data.get('phone', None)

        loggined_user=request.user
        current = utils.get_current_org_role(request.user.id)
        requested = utils.get_current_org_role(pk)

        try:
            user = models.User.objects.get(id=pk,is_active=True)
        except:
            return Response(data={"detail": "Requested user does not exists"}, status=status.HTTP_404_NOT_FOUND)
        
        if role == models.Role.RoleName.superadmin:
            if current.role != models.Role.RoleName.superadmin:
                return Response(data={"detail": "You do not have the permission to modify role to Super Admin"}, status=status.HTTP_403_FORBIDDEN)
            if requested.organization:
                return Response(data={"detail": "Only enterprise users can be Super Admin"}, status=status.HTTP_403_FORBIDDEN)                

        if current.role == models.Role.RoleName.superadmin:
            utils.update_user_detail(user, first_name, last_name, phone, loggined_user)
            utils.update_user_role(user, role, loggined_user)
            return Response(data={"detail": "User details has been updated."}, status=status.HTTP_200_OK)
        
        elif current.role == models.Role.RoleName.admin:
            if requested.organization is None:
                return Response(data={"detail": "You do not have the permission to modify enterprise users"}, status=status.HTTP_403_FORBIDDEN)
            if str(requested.organization.id) != str(current.organization.id):
                return Response(data={"detail": "User does not belong to your organization"}, status=status.HTTP_400_BAD_REQUEST)
            
            utils.update_user_detail(user, first_name, last_name, phone, loggined_user)
            utils.update_user_role(user, role, loggined_user)
            return Response(data={"detail": "User details has been updated."}, status=status.HTTP_200_OK)

        else:
            try:
                if int(pk) != int(request.user.id):
                    return Response(data={"detail": "You do not have permission to modify another users"}, status=status.HTTP_403_FORBIDDEN)            
                if current.role != role:
                    return Response(data={"detail": "You do not have permission to change your role"}, status=status.HTTP_403_FORBIDDEN)
            except:
                return Response(data={"detail": "You do not have permission to modify another users"}, status=status.HTTP_403_FORBIDDEN)
            utils.update_user_detail(user, first_name, last_name, phone, loggined_user)
            return Response(data={"detail": "User details has been updated."}, status=status.HTTP_200_OK)
    
    @extend_schema(tags=['users'],responses = {202: dict,400: dict, 403: dict, 404: dict})
    def destroy(self, request, pk):
        if int(pk)==int(request.user.id): return Response(data={"detail": "Permission Denied. This Action Cannot be Performed"}, status=status.HTTP_403_FORBIDDEN)
        requested = utils.get_current_org_role(pk)
        current = utils.get_current_org_role(request.user.id)
        if (current.role == models.Role.RoleName.admin) and (requested.organization != current.organization):
            return Response(data={"detail": "User does not belong to your organization"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.get_queryset().get(pk=pk)
        except models.User.DoesNotExist:
            return Response(data={"detail": f"{pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        user = utils.delete_user(pk,request.user)
        fullname = user.first_name+' '+user.last_name
        sites_functions.create_activity_log(
            user=request.user, 
            activity= {
                "activity": "Deleted user", 
                "message":f"Deleted user <strong>{fullname}</strong>",
                "old_value": user.first_name, 
                "new_value": user.first_name
            }
        )
        return Response(data={"status": "User deleted successfully"}, status=status.HTTP_202_ACCEPTED)

