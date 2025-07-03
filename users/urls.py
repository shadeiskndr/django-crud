from django.urls import path
from .views import RegisterView

app_name = "users"

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # You would add login, logout, password_reset URLs here
    # (or include them from a library like dj-rest-auth)
]
