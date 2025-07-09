from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, UserSerializer
from .models import CustomUser
from .permissions import IsAdmin
from .docs import (
    JWT_TOKEN_OBTAIN_SCHEMA,
    USER_REGISTRATION_SCHEMA,
    USER_LIST_SCHEMA,
    USER_ROLE_UPDATE_SCHEMA
)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role

        return token

@JWT_TOKEN_OBTAIN_SCHEMA
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@USER_REGISTRATION_SCHEMA
class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,) # Anyone can register
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # The UserSerializer will now include the default role in the response
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "User created successfully. You can now log in."
        }, status=status.HTTP_201_CREATED)

@USER_LIST_SCHEMA
class UserListView(generics.ListAPIView):
    """
    API endpoint that lists all users.
    Only accessible by users with the 'ADMIN' role.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin] # Enforce admin role

@USER_ROLE_UPDATE_SCHEMA
class UserRoleUpdateView(generics.UpdateAPIView):
    """
    API endpoint for admins to update user roles.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        new_role = request.data.get('role')
        
        if not new_role:
            return Response({'error': 'Role field is required'}, status=400)
        
        if new_role in [choice[0] for choice in CustomUser.Role.choices]:
            old_role = user.role
            user.role = new_role
            user.save()
            return Response({
                'message': f'User role updated from {old_role} to {new_role}',
                'user': UserSerializer(user).data
            }, status=200)
        
        return Response({
            'error': 'Invalid role',
            'valid_roles': [choice[0] for choice in CustomUser.Role.choices]
        }, status=400)

