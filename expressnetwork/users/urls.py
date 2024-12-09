from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter

from django.urls import path, include
from users import views

router = DefaultRouter()
router.register(r'user', views.UserView, basename='users')
router.register(r'hub', views.OrganizationView, basename='hubs')

urlpatterns = [
    path('', include(router.urls)),
    # path('login', views.LoginView.as_view(), name='login'),
    path('refresh', jwt_views.TokenRefreshView.as_view(), name='refresh'),
    # path('logout', views.LogoutView.as_view(), name='logout'),
    # path('profile/info', views.ProfileInfoView.as_view(), name='user-profile-info'),
    # path('reset-password', views.ResetPasswordView.as_view(), name='reset-password'),
    # path('reset-password/confirm', views.ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
    # path('reset-password/expire', views.ResetPasswordExpire.as_view(), name='reset-password-expire'),
    # path('change-password', views.ChangePasswordView.as_view(), name='change-password'),
    # path('Loggedin-user-details', views.LoggedinUserDetails.as_view(), name='Loggedin-user-details'),
    # path('Clear-Loggedin-user-details', views.ClearLoggedinUserDetails.as_view(), name='Clear-Loggedin-user-details'),
    # path('users-search', views.UsersGlobalSearchView.as_view(), name='users-search'),
    # path('activity-log', views.ActivityLog.as_view(), name='activity_log'),
    # path('log-search', views.LogSearch.as_view(), name='log_search'),
]
