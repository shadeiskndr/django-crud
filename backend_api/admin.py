from django.contrib import admin
from .models import (
    Movie,
    Genre,
    SpokenLanguage,
    OriginCountry,
    ProductionCompany,
    ProductionCountry,
    Video,
    MovieGenre,
    MovieSpokenLanguage,
    MovieOriginCountry,
    MovieProductionCompany,
    MovieProductionCountry,
    MovieVideo,
)

# ──────────────  Lookup models  ──────────────
admin.site.register(Genre)
admin.site.register(SpokenLanguage)
admin.site.register(OriginCountry)
admin.site.register(ProductionCompany)
admin.site.register(ProductionCountry)
admin.site.register(Video)


# ──────────────  Through-table inlines  ──────────────
class MovieGenreInline(admin.TabularInline):
    model = MovieGenre
    extra = 0


class MovieSpokenLanguageInline(admin.TabularInline):
    model = MovieSpokenLanguage
    extra = 0


class MovieOriginCountryInline(admin.TabularInline):
    model = MovieOriginCountry
    extra = 0


class MovieProductionCompanyInline(admin.TabularInline):
    model = MovieProductionCompany
    extra = 0


class MovieProductionCountryInline(admin.TabularInline):
    model = MovieProductionCountry
    extra = 0


class MovieVideoInline(admin.TabularInline):
    model = MovieVideo
    extra = 0


# ──────────────  Movie admin  ──────────────
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "release_date", "vote_average", "popularity", "runtime")
    list_filter = ("video", "release_date", "original_language")
    search_fields = ("title", "original_title", "overview")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    inlines = (
        MovieGenreInline,
        MovieSpokenLanguageInline,
        MovieOriginCountryInline,
        MovieProductionCompanyInline,
        MovieProductionCountryInline,
        MovieVideoInline,
    )
