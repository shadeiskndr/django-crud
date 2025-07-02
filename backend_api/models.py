from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# ────────────────────────────────────────
#  Lookup / reference tables
# ────────────────────────────────────────
class Genre(models.Model):
    """TMDB genre catalogue entry."""
    tmdb_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class SpokenLanguage(models.Model):
    iso_639_1 = models.CharField(max_length=7, primary_key=True)
    english_name = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100, null=True)

    class Meta:
        ordering = ("english_name", "name")

    def __str__(self):
        return self.english_name or self.name


class OriginCountry(models.Model):
    iso_3166_1 = models.CharField(max_length=5, primary_key=True)

    def __str__(self):
        return self.iso_3166_1


class ProductionCompany(models.Model):
    tmdb_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    origin_country = models.CharField(max_length=5, blank=True, null=True)
    logo_path = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class ProductionCountry(models.Model):
    iso_3166_1 = models.CharField(max_length=5, primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Video(models.Model):
    video_id = models.CharField(max_length=40, primary_key=True)
    key = models.CharField(max_length=100)
    name = models.CharField(max_length=255, null=True)
    site = models.CharField(max_length=30)
    size = models.PositiveIntegerField()
    type = models.CharField(max_length=50)
    official = models.BooleanField(default=False, null=True)
    published_at = models.DateTimeField()

    class Meta:
        ordering = ("-published_at",)

    def __str__(self):
        return f"{self.name} ({self.site})"


# ────────────────────────────────────────
#  Main Movie table (scalar columns only)
# ────────────────────────────────────────
class Movie(models.Model):
    # Basic movie info
    adult = models.BooleanField(default=False, null=True)
    title = models.TextField()
    original_title = models.TextField()
    video = models.BooleanField(default=False, null=True)
    budget = models.BigIntegerField(null=True, blank=True)
    revenue = models.BigIntegerField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    status = models.TextField(blank=True)
    imdb_id = models.CharField(max_length=20, blank=True, null=True)
    tagline = models.TextField(blank=True, null=True)
    homepage = models.URLField(blank=True, max_length=500, null=True)
    overview = models.TextField(blank=True, null=True)
    popularity = models.FloatField(null=True, blank=True)
    vote_count = models.IntegerField(null=True, blank=True)
    vote_average = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    release_date = models.DateField(null=True, blank=True)
    original_language = models.CharField(max_length=10, blank=True)
    poster_path = models.TextField(blank=True)
    backdrop_path = models.TextField(blank=True, null=True)

    # Collection info  (flattened)
    collection_id = models.IntegerField(null=True, blank=True)
    collection_name = models.TextField(blank=True, null=True)
    collection_poster_path = models.TextField(blank=True, null=True)
    collection_backdrop_path = models.TextField(blank=True, null=True)

    # External IDs (flattened)
    external_imdb_id = models.CharField(max_length=50, blank=True, null=True)
    external_twitter_id = models.CharField(max_length=50, blank=True, null=True)
    external_facebook_id = models.CharField(max_length=50, blank=True, null=True)
    external_wikidata_id = models.CharField(max_length=50, blank=True, null=True)
    external_instagram_id = models.CharField(max_length=50, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-many relations via explicit through-tables
    genres = models.ManyToManyField(
        Genre, through="MovieGenre", related_name="movies"
    )
    spoken_languages = models.ManyToManyField(
        SpokenLanguage, through="MovieSpokenLanguage", related_name="movies"
    )
    origin_countries = models.ManyToManyField(
        OriginCountry, through="MovieOriginCountry", related_name="movies"
    )
    production_companies = models.ManyToManyField(
        ProductionCompany, through="MovieProductionCompany", related_name="movies"
    )
    production_countries = models.ManyToManyField(
        ProductionCountry, through="MovieProductionCountry", related_name="movies"
    )
    videos = models.ManyToManyField(
        Video, through="MovieVideo", related_name="movies"
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["release_date"]),
            models.Index(fields=["vote_average"]),
            models.Index(fields=["popularity"]),
        ]

    def __str__(self):
        year = self.release_date.year if self.release_date else "Unknown"
        return f"{self.title} ({year})"


# ────────────────────────────────────────
#  Through tables
# ────────────────────────────────────────
class MovieGenre(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("movie", "genre")


class MovieSpokenLanguage(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    language = models.ForeignKey(SpokenLanguage, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("movie", "language")


class MovieOriginCountry(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    country = models.ForeignKey(OriginCountry, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("movie", "country")


class MovieProductionCompany(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    company = models.ForeignKey(ProductionCompany, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("movie", "company")


class MovieProductionCountry(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    country = models.ForeignKey(ProductionCountry, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("movie", "country")


class MovieVideo(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("movie", "video")
