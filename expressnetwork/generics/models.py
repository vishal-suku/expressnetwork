from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _ 
from generics import mixins
from django.utils import timezone
# Create your models here.


class User(AbstractUser):
    username = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={'unique': "A user with that username already exists."})

    EMAIL_FIELD = 'username'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = "Users"


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


class Organization(mixins.GenericModelMixin):
    name = models.CharField(null=False, max_length=50, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.BigIntegerField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name="created_org")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,related_name="updated_org")
    sftp = models.BooleanField(default=False)
    sftp_username = models.CharField(max_length=50, default='')
    sftp_password = models.CharField(max_length=50, default='')
    sftp_host     = models.CharField(max_length=50, default='')
    sftp_port     = models.CharField(max_length=50, default='80')
    sftp_path     = models.CharField(max_length=50, default='')
    is_active     = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Organizations"


class Role(mixins.GenericModelMixin):
    class RoleName(models.TextChoices):
        """
        -----------
        Permissions
        -----------
        user      : see schedules
        scheduler : see schedules + create schedules
        manager   : see schedules + create schedules + add resources
        admin     : everything in the organization
        """

        superadmin = "superadmin", "Super Admin"
        admin = "admin", "Organization Admin"
        manager = "manager", "Manager"
        scheduler = "scheduler", "Scheduler"
        user = "user", "User"
        otheruser = "aya", "Aya"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="role")
    role = models.CharField(null=True,
                            blank=True,
                            max_length=50,
                            choices=RoleName.choices,
                            default=RoleName.admin)
    organization = models.ForeignKey(Organization,
                                     null=True,
                                     blank=True,
                                     on_delete=models.CASCADE)
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

class TryLog(mixins.GenericModelMixin):
    email = models.CharField(max_length=200, null=True,blank=True)
    try_count = models.IntegerField(default=1)
  

class UserUpdation(mixins.GenericModelMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,related_name="user_updation")
    update_type = models.CharField(max_length=50, null=True, blank=True)

        
    