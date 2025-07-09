from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

# Movie ViewSet Documentation
MOVIE_VIEWSET_SCHEMA = extend_schema_view(
    list=extend_schema(
        summary="List Movies",
        description="Retrieve a paginated list of movies with optional search and filtering. No authentication required.",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search movies by title, original title, or overview',
            ),
            OpenApiParameter(
                name='genre',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by genre name (case-insensitive)',
            ),
            OpenApiParameter(
                name='year',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by release year',
            ),
            OpenApiParameter(
                name='min_rating',
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
                description='Minimum vote average (0-10)',
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Order results by field. Prefix with "-" for descending order.',
            ),
        ],
        responses={
            200: {
                'description': 'Paginated list of movies',
            }
        },
        tags=['Movies']
    ),
    create=extend_schema(
        summary="Create Movie",
        description="Create a new movie with relational data. Admin access required.",
        responses={
            201: {'description': 'Movie created successfully'},
            400: {'description': 'Invalid data provided'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Admin access required'},
        },
        tags=['Movies']
    ),
    retrieve=extend_schema(
        summary="Get Movie Details",
        description="Retrieve detailed information about a specific movie including all related data.",
        responses={
            200: {'description': 'Movie details with full relations'},
            404: {'description': 'Movie not found'},
        },
        tags=['Movies']
    ),
    update=extend_schema(
        summary="Update Movie",
        description="Update all fields of a movie. Admin access required.",
        tags=['Movies']
    ),
    partial_update=extend_schema(
        summary="Partially Update Movie",
        description="Update specific fields of a movie. Admin access required.",
        tags=['Movies']
    ),
    destroy=extend_schema(
        summary="Delete Movie",
        description="Delete a movie and all its relationships. Admin access required.",
        tags=['Movies']
    ),
)

# Movie Stats Documentation
MOVIE_STATS_SCHEMA = extend_schema(
    summary="Get Database Statistics",
    description="Retrieve comprehensive statistics about the movie database.",
    responses={
        200: {
            'description': 'Database statistics',
        }
    },
    tags=['Movies', 'Analytics']
)
