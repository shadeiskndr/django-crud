from django.urls import path
from backend_api import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('test/', views.api_test, name='api_test'),
    path('health/', views.health_check, name='health_check'),
]
