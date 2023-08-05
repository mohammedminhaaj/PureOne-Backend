from django.urls import path
from . import views

urlpatterns = [
    path('auth/login/credential/', views.credential_login, name='credential_login'),
    path('auth/login/otp/', views.otp_login, name='otp_login'),
    path('auth/login/otp/verify/', views.verify_otp, name='verify_otp'),
    path('auth/sign-up/', views.create_account, name='create_account'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/forgot-password/', views.forgot_password, name='forgot_password'),
    path('auth/update-profile/', views.update_profile, name='update_profile'),

    path('add-user-location/', views.add_edit_user_location, name='add_user_location'),
    path('edit-user-location/<str:user_location_id>/', views.add_edit_user_location, name='edit_user_location'),
    path('delete-user-location/<str:user_location_id>/', views.delete_user_location, name='delete_user_location'),
]
