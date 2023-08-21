from . import views
from django.urls import path

urlpatterns = [
    path('get-home-screen/', views.get_home_screen, name='get_home_screen'),
    path('add-fcm-token/', views.add_fcm_token, name='add_fcm_token'),
]