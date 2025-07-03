from django.urls import path
from .views import RegisterView, MyTokenObtainPairView # <-- Import the new view
from rest_framework_simplejwt.views import TokenRefreshView

app_name = "users"

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
