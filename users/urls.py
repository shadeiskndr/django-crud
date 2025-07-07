from django.urls import path
from .views import RegisterView, MyTokenObtainPairView, UserListView, UserRoleUpdateView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = "users"

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/role/', UserRoleUpdateView.as_view(), name='user-role-update'),
]
