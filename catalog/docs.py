from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.types import OpenApiTypes

# Catalog Entries Documentation
CATALOG_ENTRIES_SCHEMA = extend_schema_view(
    list=extend_schema(
        summary="List User's Catalog Entries",
        description="Retrieve all movies in the user's personal catalog with their status and notes.",
        tags=['Personal Catalog']
    ),
    create=extend_schema(
        summary="Add Movie to Catalog",
        description="Add a movie to the user's personal catalog with a specific status.",
        tags=['Personal Catalog']
    ),
    retrieve=extend_schema(
        summary="Get Catalog Entry Details",
        description="Retrieve detailed information about a specific catalog entry.",
        tags=['Personal Catalog']
    ),
    update=extend_schema(
        summary="Update Catalog Entry",
        description="Update a catalog entry's status, rating, or notes.",
        tags=['Personal Catalog']
    ),
    partial_update=extend_schema(
        summary="Partially Update Catalog Entry",
        description="Update specific fields of a catalog entry.",
        tags=['Personal Catalog']
    ),
    destroy=extend_schema(
        summary="Remove from Catalog",
        description="Remove a movie from the user's personal catalog.",
        tags=['Personal Catalog']
    ),
    bookmarked=extend_schema(
        summary="Get Bookmarked Movies",
        description="Retrieve all movies marked as bookmarked by the user.",
        tags=['Personal Catalog']
    ),
    watched=extend_schema(
        summary="Get Watched Movies",
        description="Retrieve all movies marked as watched by the user.",
        tags=['Personal Catalog']
    ),
    want_to_watch=extend_schema(
        summary="Get Want-to-Watch Movies",
        description="Retrieve all movies in the user's want-to-watch list.",
        tags=['Personal Catalog']
    ),
    bookmark=extend_schema(
        summary="Quick Bookmark Movie",
        description="Quickly bookmark a movie with optional notes.",
        tags=['Personal Catalog']
    ),
    mark_watched=extend_schema(
        summary="Mark Movie as Watched",
        description="Mark a movie as watched with optional rating and notes.",
        tags=['Personal Catalog']
    ),
    add_to_watchlist=extend_schema(
        summary="Add to Watchlist",
        description="Add a movie to the want-to-watch list.",
        tags=['Personal Catalog']
    ),
    remove=extend_schema(
        summary="Remove Movie from Catalog",
        description="Remove a movie from the user's catalog entirely.",
        tags=['Personal Catalog']
    ),
    stats=extend_schema(
        summary="Get Catalog Statistics",
        description="Retrieve statistics about the user's movie catalog.",
        tags=['Personal Catalog']
    ),
)

# Movie Collections Documentation
MOVIE_COLLECTIONS_SCHEMA = extend_schema_view(
    list=extend_schema(
        summary="List Movie Collections",
        description="Retrieve user's own collections and public collections from other users.",
        tags=['Movie Collections']
    ),
    create=extend_schema(
        summary="Create Movie Collection",
        description="Create a new movie collection.",
        tags=['Movie Collections']
    ),
    retrieve=extend_schema(
        summary="Get Collection Details",
        description="Retrieve detailed information about a specific movie collection.",
        tags=['Movie Collections']
    ),
    update=extend_schema(
        summary="Update Collection",
        description="Update a movie collection's details.",
        tags=['Movie Collections']
    ),
    partial_update=extend_schema(
        summary="Partially Update Collection",
        description="Update specific fields of a movie collection.",
        tags=['Movie Collections']
    ),
    destroy=extend_schema(
        summary="Delete Collection",
        description="Delete a movie collection.",
        tags=['Movie Collections']
    ),
    my_collections=extend_schema(
        summary="Get My Collections",
        description="Retrieve only the current user's movie collections.",
        tags=['Movie Collections']
    ),
    add_movie=extend_schema(
        summary="Add Movie to Collection",
        description="Add a movie to a specific collection.",
        tags=['Movie Collections']
    ),
    remove_movie=extend_schema(
        summary="Remove Movie from Collection",
        description="Remove a movie from a specific collection.",
        tags=['Movie Collections']
    ),
)
