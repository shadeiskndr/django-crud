from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.types import OpenApiTypes

# Review ViewSet Documentation
REVIEW_VIEWSET_SCHEMA = extend_schema_view(
    list=extend_schema(
        summary="List Reviews",
        description="Retrieve a paginated list of published reviews. Users can see their own reviews in all statuses.",
        tags=['Reviews']
    ),
    create=extend_schema(
        summary="Create Review",
        description="Create a new movie review. Users can only have one review per movie.",
        tags=['Reviews']
    ),
    retrieve=extend_schema(
        summary="Get Review Details",
        description="Retrieve detailed information about a specific review.",
        tags=['Reviews']
    ),
    update=extend_schema(
        summary="Update Review",
        description="Update a review. Only the author can update their own review.",
        tags=['Reviews']
    ),
    partial_update=extend_schema(
        summary="Partially Update Review",
        description="Update specific fields of a review. Only the author can update their own review.",
        tags=['Reviews']
    ),
    destroy=extend_schema(
        summary="Delete Review",
        description="Delete a review. Only the author can delete their own review.",
        tags=['Reviews']
    ),
    my_reviews=extend_schema(
        summary="Get My Reviews",
        description="Get current user's reviews (all statuses)",
        tags=['Reviews']
    ),
    publish=extend_schema(
        summary="Publish Review",
        description="Publish a draft review",
        tags=['Reviews']
    ),
    featured=extend_schema(
        summary="Get Featured Reviews",
        description="Get reviews that have been featured by moderators",
        tags=['Reviews']
    ),
)

# Review Moderation ViewSet Documentation
REVIEW_MODERATION_SCHEMA = extend_schema_view(
    list=extend_schema(
        summary="List Reviews for Moderation",
        description="Retrieve reviews for moderation purposes. Only accessible by moderators and admins.",
        tags=['Review Moderation']
    ),
    retrieve=extend_schema(
        summary="Get Review for Moderation",
        description="Retrieve a specific review for moderation purposes.",
        tags=['Review Moderation']
    ),
    update=extend_schema(
        summary="Moderate Review",
        description="Update review moderation status, feature status, or add moderation notes.",
        tags=['Review Moderation']
    ),
    partial_update=extend_schema(
        summary="Partially Moderate Review",
        description="Update specific moderation fields of a review.",
        tags=['Review Moderation']
    ),
    pending=extend_schema(
        summary="Get Pending Reviews",
        description="Get reviews that need moderation attention (reported or newly published).",
        tags=['Review Moderation']
    ),
    feature=extend_schema(
        summary="Feature/Unfeature Review",
        description="Mark a review as featured or remove featured status.",
        tags=['Review Moderation']
    ),
    hide=extend_schema(
        summary="Hide Review",
        description="Hide a review from public view with moderation notes.",
        tags=['Review Moderation']
    ),
    restore=extend_schema(
        summary="Restore Review",
        description="Restore a previously hidden review to published status.",
        tags=['Review Moderation']
    ),
)

# Review Vote ViewSet Documentation
REVIEW_VOTE_SCHEMA = extend_schema_view(
    list=extend_schema(
        summary="List My Review Votes",
        description="Retrieve current user's votes on reviews.",
        tags=['Review Votes']
    ),
    create=extend_schema(
        summary="Vote on Review",
        description="Vote on a review as helpful or not helpful. Users cannot vote on their own reviews.",
        tags=['Review Votes']
    ),
    retrieve=extend_schema(
        summary="Get Vote Details",
        description="Retrieve details about a specific vote.",
        tags=['Review Votes']
    ),
    update=extend_schema(
        summary="Update Vote",
        description="Change your vote on a review.",
        tags=['Review Votes']
    ),
    partial_update=extend_schema(
        summary="Partially Update Vote",
        description="Update specific fields of your vote.",
        tags=['Review Votes']
    ),
    destroy=extend_schema(
        summary="Remove Vote",
        description="Remove your vote from a review.",
        tags=['Review Votes']
    ),
)

# Review Report ViewSet Documentation
REVIEW_REPORT_SCHEMA = extend_schema_view(
    list=extend_schema(
        summary="List Review Reports",
        description="List review reports. Regular users see only their own reports, moderators see all reports.",
        tags=['Review Reports']
    ),
    create=extend_schema(
        summary="Report Review",
        description="Report a review for inappropriate content. Users cannot report their own reviews.",
        tags=['Review Reports']
    ),
    retrieve=extend_schema(
        summary="Get Report Details",
        description="Retrieve details about a specific report.",
        tags=['Review Reports']
    ),
    update=extend_schema(
        summary="Update Report",
        description="Update a report (mainly for moderators to resolve reports).",
        tags=['Review Reports']
    ),
    partial_update=extend_schema(
        summary="Partially Update Report",
        description="Update specific fields of a report.",
        tags=['Review Reports']
    ),
    destroy=extend_schema(
        summary="Delete Report",
        description="Delete a report.",
        tags=['Review Reports']
    ),
    pending=extend_schema(
        summary="Get Pending Reports",
        description="Get unresolved reports. Only accessible by moderators and admins.",
        tags=['Review Reports']
    ),
    resolve=extend_schema(
        summary="Resolve Report",
        description="Mark a report as resolved with resolution notes. Only accessible by moderators and admins.",
        tags=['Review Reports']
    ),
)
