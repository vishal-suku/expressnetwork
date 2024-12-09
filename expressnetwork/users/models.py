from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils.translation import gettext_lazy as _ 
from generics import mixins
from django.utils import timezone
# Create your models here.


class Organization(mixins.GenericModelMixin):
    name = models.CharField(null=False, max_length=50, unique=True)
    email = models.EmailField(blank=False)
    phone = models.BigIntegerField(null=True)
    location = models.CharField(max_length=50, null=False)
    password = models.CharField(max_length=50, null=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name="created_org")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,related_name="updated_org")
    sftp = models.BooleanField(default=False)
    sftp_path     = models.CharField(max_length=50, default='')
    is_active     = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Organizations"


class Profile(mixins.GenericModelMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.BigIntegerField(null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='created_user')
    updated_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='updated_user')

    def __str__(self):
        return str(self.user.username)

    class Meta:
        verbose_name_plural = "Profiles"



class Role(mixins.GenericModelMixin):
    class RoleName(models.TextChoices):
        """
        -----------
        Permissions
        -----------
        user      : raise a ticket
        admin : see tickets + assign
        technician   : verify and fix the issue
        superadmin     : everything in the organization
        """

        superadmin = "superadmin", "Super Admin"
        admin = "admin", "Organization Admin"
        technician = "technician", "Technician"
        user = "user", "User"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="role")
    role = models.CharField(null=True,
                            blank=True,
                            max_length=50,
                            choices=RoleName.choices,
                            default=RoleName.admin)
    is_active     = models.BooleanField(default=True)
    def __str__(self):
        return str(self.id)+" / "+str(self.user.username)

    class Meta:
        verbose_name_plural = "Roles"


class Activity(mixins.GenericModelMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Activities"


class UserLog(mixins.GenericModelMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=100, null=False)
    version = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "UserLog"


class UserSession(mixins.GenericModelMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_start_time = models.DateTimeField()
    session_end_time = models.DateTimeField(null=True, blank=True)
    inactive_hours = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.id)
    
    def duration(self):
            return self.session_end_time - self.session_start_time  
    class Meta:
        verbose_name_plural = "UserLog"
