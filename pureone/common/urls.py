from . import views
from django.urls import path

urlpatterns = [
    path('get-home-screen/', views.get_home_screen, name='get_home_screen'),
]