from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from . import models

def validate_role(role_value):
    for choice, value in models.Role.RoleName.choices:
        if choice == role_value:
            return choice
    raise serializers.ValidationError("role must be a valid OrganizationalRole")

def validate_organization(value):
    try:
        organization = models.Organization.objects.get(pk=value)
    except models.Organization.DoesNotExist:
        raise serializers.ValidationError("organization must be a valid OrganizationalRole id")
    return organization

def validate_user(value):
    try:
        user = models.User.objects.get(pk=value)
    except models.User.DoesNotExist:
        raise serializers.ValidationError("user must be a valid id")
    return user


class HubInfoModelSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=2, max_length=50, required=True)
    email = serializers.EmailField(min_length=1, max_length=50, required=True)
    phone = serializers.IntegerField(
        min_value=1000000000, max_value=9999999999, required=False, allow_null=True, error_messages={'min_value': _('Enter a valid Phone number.'), 'max_value': _('Enter a valid Phone number.')})
    location = serializers.CharField(required=True)

class LogoutRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField(min_length=100,max_length=300,required=True)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=8, max_length=100, required=True)


class UserCreateSerializer(EmailSerializer):
    first_name = serializers.CharField(min_length=2, max_length=50, required=True)
    last_name = serializers.CharField(min_length=1, max_length=50, required=True)
    phone = serializers.IntegerField(
        min_value=1000000000, max_value=9999999999, required=False, allow_null=True, error_messages={'min_value': _('Enter a valid Phone number.'), 'max_value': _('Enter a valid Phone number.')})


class UserInfoModelSerializer(serializers.ModelSerializer):
    def get_phone(self, query_set) -> str:
        profile = models.Profile.objects.filter(user=query_set).first()
        if profile is None:
            return profile
        return profile.phone


    def get_organization(self, queryset) -> dict:
        organization_role = models.Role.objects.filter(user=queryset).first()
        if organization_role is None:
            return organization_role
        if organization_role.organization is None:
            return {"sftp_enabled":None,"role": {"id":"superadmin", "name": "Super Admin"}, "name": None, "id":None}        
        return {"sftp_enabled":organization_role.organization.sftp,"role": { "id": organization_role.role, "name":organization_role.get_role_display()}, "name": organization_role.organization.name, "id":organization_role.organization.id}

    email = serializers.CharField(source='username')
    phone = serializers.SerializerMethodField(method_name='get_phone')
    organization = serializers.SerializerMethodField(method_name='get_organization')
    class Meta:
        model  = models.User
        fields = ['id','first_name', 'last_name','email', 'organization', 'phone']


class SuperUserListModelSerializer(UserInfoModelSerializer):
    class Meta:
        model  = models.User
        fields = ['id', 'first_name', 'last_name', 'email']


class KeyPasswordSerializer(serializers.Serializer):
    key = serializers.CharField(min_length=100, max_length=300, required=True)
    password = serializers.CharField(min_length=8, max_length=30, required=True)


class KeySerializer(serializers.Serializer):
    key = serializers.CharField(min_length=100, max_length=300, required=True)


class UserIDSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(
        min_value=1, max_value=None, required=True)


class UserUpdateSerializer(UserIDSerializer):
    first_name = serializers.CharField(min_length=2, max_length=50, required=True)
    last_name = serializers.CharField(min_length=1, max_length=50, required=True)
    phone = serializers.IntegerField(min_value=1000000000, max_value=9999999999, required=False, allow_null=True, error_messages={'min_value': _('Enter a valid Phone number.'), 'max_value': _('Enter a valid Phone number.')})


class UserIdSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1, max_value=None, required=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        min_length=8, max_length=30, required=True)
    new_password = serializers.CharField(
        min_length=8, max_length=30, required=True)


class UserListModelSerializer(serializers.ModelSerializer):
    class Meta:
        model  = models.User
        fields = ['id', 'first_name', 'last_name', 'username','sftp']


# class OrganizationNameListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model  = models.Organization
#         fields = ['id', 'name']


class CreateUserSerializer(UserCreateSerializer): 
    role         = serializers.CharField(required=True,validators=[validate_role])
    organization = serializers.UUIDField(required=False,validators=[validate_organization])


class UpdateOrganizationUserSerializer(serializers.Serializer):
    role         = serializers.CharField(required=True,validators=[validate_role])
    first_name = serializers.CharField(min_length=2, max_length=50, required=True)
    last_name = serializers.CharField(min_length=1, max_length=50, required=True)
    phone = serializers.IntegerField(min_value=1000000000, max_value=9999999999, required=False, allow_null=True, error_messages={'min_value': _('Enter a valid Phone number.'), 'max_value': _('Enter a valid Phone number.')})


class UserContactSerializer(serializers.ModelSerializer):
    def get_phone(self, query_set) -> str:
        profile = models.Profile.objects.filter(user=query_set).first()
        if profile is None:
            return profile
        return profile.phone

    email = serializers.CharField(source='username')
    phone = serializers.SerializerMethodField(method_name='get_phone')
    class Meta:
        model  = models.User
        fields = ['id','first_name', 'last_name','email', 'phone']


class UserDetailsSerializer(serializers.ModelSerializer):
    user = serializers.CharField(min_length=3, max_length=50, required=True)
    ip_address = serializers.CharField(min_length=3, max_length=50, required=True)
    version = serializers.CharField(min_length=1, max_length=50, required=True)

    class Meta:
        model  = models.UserLog
        fields = ['id', 'user', 'ip_address', 'version']


class UserprofileModelSerializer(serializers.ModelSerializer):
    def get_organization(self, queryset) -> dict:
        organization_role = models.Role.objects.filter(user=queryset.user).first()
        if organization_role is None:
            return organization_role
        if organization_role.organization is None:
            return {"sftp_enabled":None,"role": organization_role.role, "name": None, "id":None}        
        return {"sftp_enabled":organization_role.organization.sftp,"role": organization_role.role, "name": organization_role.organization.name, "id":organization_role.organization.id}
    id =  serializers.CharField(source='user.id')
    email = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    organization = serializers.SerializerMethodField(method_name='get_organization')
    class Meta:
        model  = models.Profile
        fields = ['id','first_name', 'last_name','email', 'organization', 'phone']


class Searchserializer(serializers.Serializer):
    keyword = serializers.CharField(required=True)


class UserSearchSerializer(serializers.ModelSerializer):
    def get_phone(self, query_set) -> str:
        profile = models.Profile.objects.filter(user=query_set).first()
        if profile is None:
            return profile
        return profile.phone

    def get_organization(self, queryset) -> dict:
        organization_role = models.Role.objects.filter(user=queryset).first()
        if organization_role is None:
            return organization_role
        if organization_role.organization is None:
            return {"sftp_enabled":None,"role": {"id":"superadmin", "name": "Super Admin"}, "name": None, "id":None}        
        return {"sftp_enabled":organization_role.organization.sftp,"role": { "id": organization_role.role, "name":organization_role.get_role_display()}, "name": organization_role.organization.name, "id":organization_role.organization.id}

    email = serializers.CharField(source='username')
    phone = serializers.SerializerMethodField(method_name='get_phone')
    organization = serializers.SerializerMethodField(method_name='get_organization')
    class Meta:
        model  = models.User
        fields = ['id','first_name', 'last_name','email', 'organization', 'phone']


class UserLogRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)


# class UserLogSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(source="user.first_name")
#     class Meta:
#         model  = sites_models.UserActivityLog
#         fields = ['id', 'first_name', 'activity', 'created_at']


# class UserLogSearchSerializer(serializers.Serializer):
#     user_id = serializers.CharField(required=True)
#     keyword = serializers.CharField(required=False)

