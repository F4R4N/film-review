from django.urls import path
from .views import (
    RegisterView, ChangePasswordView, UpdateProfileView, LogoutView,
    UpdateUserImageView, DeleteProfileView, ForgotPasswordView,
    ValidateConfirmationCodeView, ResetPasswordView, UserLoginView,
    GetUserProfile)
from rest_framework_simplejwt.views import TokenRefreshView

app_name = "customauth"

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', UserLoginView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard/profile/', GetUserProfile.as_view()),
    path('dashboard/change_password/<key>/', ChangePasswordView.as_view(), name='auth_change_password'),
    path('dashboard/update_profile/<key>/', UpdateProfileView.as_view(), name='auth_update_profile'),
    path('dashboard/change_image/<key>/', UpdateUserImageView.as_view(), name='auth_image'),
    path('dashboard/logout/', LogoutView.as_view(), name='auth_logout'),
    path('dashboard/delete_profile/<key>/', DeleteProfileView.as_view(), name='auth_delete_profile'),

    path('forgot_password/', ForgotPasswordView.as_view(), name='auth_forgot_password'),
    path('confirm/', ValidateConfirmationCodeView.as_view(), name='auth_confirm'),
    path('reset_password/<key>/', ResetPasswordView.as_view(), name='auth_reset_password')

]
