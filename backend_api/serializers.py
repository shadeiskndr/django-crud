from rest_framework import serializers
from .models import (
    Movie,
    Genre,
    SpokenLanguage,
    OriginCountry,
    ProductionCompany,
    ProductionCountry,
    Video,
)

# ──────────────  Lookup serializers  ──────────────
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("tmdb_id", "name")


class SpokenLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpokenLanguage
        fields = ("iso_639_1", "english_name", "name")


class OriginCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginCountry
        fields = ("iso_3166_1",)


class ProductionCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionCompany
        fields = ("tmdb_id", "name", "origin_country", "logo_path")


class ProductionCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionCountry
        fields = ("iso_3166_1", "name")


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = (
            "video_id",
            "key",
            "name",
            "site",
            "size",
            "type",
            "official",
            "published_at",
        )


# ──────────────  Movie serializers  ──────────────
class MovieSerializer(serializers.ModelSerializer):
    """Full detail serializer (with nested read-only relations)."""
    genres = GenreSerializer(many=True, read_only=True)
    spoken_languages = SpokenLanguageSerializer(many=True, read_only=True)
    origin_countries = OriginCountrySerializer(many=True, read_only=True)
    production_companies = ProductionCompanySerializer(many=True, read_only=True)
    production_countries = ProductionCountrySerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        # include every scalar column plus the nested relations above
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class MovieListSerializer(serializers.ModelSerializer):
    """Light-weight list view: only scalar fields + genre names."""
    genres = serializers.StringRelatedField(many=True)

    class Meta:
        model = Movie
        fields = (
            "id",
            "title",
            "original_title",
            "release_date",
            "vote_average",
            "vote_count",
            "popularity",
            "poster_path",
            "genres",
            "overview",
            "runtime",
        )


# ──────────────  Create / Update  ──────────────
class MovieCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Accept scalar movie data *plus* simple id/code arrays for the m2m relations.
    Example payload fragment:
        {
          "title": "…",
          "genre_ids": [28, 12],
          "spoken_language_codes": ["en", "fr"],
          "origin_country_codes": ["US"],
          "production_company_ids": [174, 33],
          "production_country_codes": ["US"],
          "video_ids": ["6400c…"]
        }
    """
    # write-only helper fields (all optional)
    genre_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True
    )
    spoken_language_codes = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )
    origin_country_codes = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )
    production_company_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True
    )
    production_country_codes = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )
    video_ids = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )

    class Meta:
        model = Movie
        exclude = ("created_at", "updated_at", "genres", "spoken_languages",
                   "origin_countries", "production_companies",
                   "production_countries", "videos")

    # ─────  validation helpers  ─────
    def validate_vote_average(self, value):
        if value is not None and not (0 <= value <= 10):
            raise serializers.ValidationError("Vote average must be between 0 and 10.")
        return value

    def validate_runtime(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Runtime cannot be negative.")
        return value

    # ─────  create / update  ─────
    @staticmethod
    def _set_m2m(instance: Movie, attr: str, ids):
        if ids is None:
            return
        getattr(instance, attr).set(ids)

    def _handle_m2m(self, instance, validated_data):
        self._set_m2m(instance, "genres", validated_data.pop("genre_ids", None))
        self._set_m2m(instance, "spoken_languages",
                      validated_data.pop("spoken_language_codes", None))
        self._set_m2m(instance, "origin_countries",
                      validated_data.pop("origin_country_codes", None))
        self._set_m2m(instance, "production_companies",
                      validated_data.pop("production_company_ids", None))
        self._set_m2m(instance, "production_countries",
                      validated_data.pop("production_country_codes", None))
        self._set_m2m(instance, "videos", validated_data.pop("video_ids", None))

    def create(self, validated_data):
        # Pop the relational IDs from validated_data. They will be handled separately.
        genre_ids = validated_data.pop("genre_ids", None)
        spoken_language_codes = validated_data.pop("spoken_language_codes", None)
        origin_country_codes = validated_data.pop("origin_country_codes", None)
        production_company_ids = validated_data.pop("production_company_ids", None)
        production_country_codes = validated_data.pop("production_country_codes", None)
        video_ids = validated_data.pop("video_ids", None)

        # Create the movie instance with only scalar data
        movie = Movie.objects.create(**validated_data)

        # Now, set the many-to-many relationships on the created instance
        self._set_m2m(movie, "genres", genre_ids)
        self._set_m2m(movie, "spoken_languages", spoken_language_codes)
        self._set_m2m(movie, "origin_countries", origin_country_codes)
        self._set_m2m(movie, "production_companies", production_company_ids)
        self._set_m2m(movie, "production_countries", production_country_codes)
        self._set_m2m(movie, "videos", video_ids)

        return movie

    def update(self, instance, validated_data):
        # Handle m2m relations first by popping them from validated_data
        # This uses the same logic as the create method.
        genre_ids = validated_data.pop("genre_ids", None)
        spoken_language_codes = validated_data.pop("spoken_language_codes", None)
        origin_country_codes = validated_data.pop("origin_country_codes", None)
        production_company_ids = validated_data.pop("production_company_ids", None)
        production_country_codes = validated_data.pop("production_country_codes", None)
        video_ids = validated_data.pop("video_ids", None)

        # Update scalar fields on the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update the many-to-many relationships
        self._set_m2m(instance, "genres", genre_ids)
        self._set_m2m(instance, "spoken_languages", spoken_language_codes)
        self._set_m2m(instance, "origin_countries", origin_country_codes)
        self._set_m2m(instance, "production_companies", production_company_ids)
        self._set_m2m(instance, "production_countries", production_country_codes)
        self._set_m2m(instance, "videos", video_ids)

        return instance
