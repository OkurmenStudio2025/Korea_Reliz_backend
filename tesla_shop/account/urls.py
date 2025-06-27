from django.urls import path
from .views import RegisterView, VerifyCodeView, CustomTokenObtainPairView, CustomTokenRefreshView, UserDetailView, ForgotPasswordPhoneView, VerifyResetCodeView, ResetPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user/', UserDetailView.as_view(), name='user-detali'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password/phone/', ForgotPasswordPhoneView.as_view(), name='forgot-password-phone'),
    path('forgot-password/verify-code/', VerifyResetCodeView.as_view(), name='verify-reset-code'),
    path('forgot-password/reset/', ResetPasswordView.as_view(), name='reset-password')
]
