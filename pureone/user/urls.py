from django.urls import path
from . import views

urlpatterns = [
    path('login/credential/', views.credential_login, name='credential_login'),
    path('login/otp/', views.otp_login, name='otp_login'),
    path('login/otp/verify/', views.verify_otp, name='verify_otp'),
    path('sign-up/', views.create_account, name='create_account'),
    path('logout/', views.logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('update-profile/', views.update_profile, name='update_profile'),
]
