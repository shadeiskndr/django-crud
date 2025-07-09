from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes

# JWT Token Obtain Documentation
JWT_TOKEN_OBTAIN_SCHEMA = extend_schema(
    summary="Login - Obtain JWT Token",
    description="Login with email and password to get JWT access and refresh tokens with custom claims (username, email, role)",
    tags=['Authentication']
)

# User Registration Documentation
USER_REGISTRATION_SCHEMA = extend_schema(
    summary="User Registration",
    description="Register a new user account with automatic role assignment to 'USER'",
    tags=['Authentication']
)

# User List Documentation
USER_LIST_SCHEMA = extend_schema(
    summary="List All Users",
    description="Retrieve a list of all users in the system. Only accessible by users with the 'ADMIN' role.",
    tags=['User Management']
)

# User Role Update Documentation
USER_ROLE_UPDATE_SCHEMA = extend_schema(
    summary="Update User Role",
    description="Update a user's role. Only accessible by users with the 'ADMIN' role. Available roles: USER, CRITIC, MODERATOR, ADMIN",
    tags=['User Management']
)
