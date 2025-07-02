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
        self._handle_m2m(None, validated_data)   # strip helper keys first
        movie = Movie.objects.create(**validated_data)
        self._handle_m2m(movie, self.initial_data)
        return movie

    def update(self, instance, validated_data):
        self._handle_m2m(instance, validated_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._handle_m2m(instance, self.initial_data)
        return instance
