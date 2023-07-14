from . import views
from django.urls import path

urlpatterns = [
    path('get-initial-state/', views.get_initial_state, name='get_initial_state'),
]