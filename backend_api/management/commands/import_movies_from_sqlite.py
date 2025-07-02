import sqlite3
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models

from backend_api.models import (
    Genre,
    SpokenLanguage,
    OriginCountry,
    ProductionCompany,
    ProductionCountry,
    Video,
    Movie,
)

# ─────────────────────────────────────────────────────────────
# Tuneables
# ─────────────────────────────────────────────────────────────
# rows per bulk_create / executemany
BATCH = 10_000          # larger batches = fewer round-trips
# rows fetched from SQLite at once
CHUNK = 10_000


class Command(BaseCommand):
    """
    Import the normalised movies.db (written by json_to_sqlite_filtered.py)
    into the Django models.  The whole import runs inside one single
    transaction and relies on bulk_create for both entity rows and all
    many-to-many through rows.
    """

    help = "Import movies & related tables from the normalised SQLite dump."

    # ─────────────────────────────────────────────────────────
    # arg parsing
    # ─────────────────────────────────────────────────────────
    def add_arguments(self, parser):
        parser.add_argument(
            "sqlite_file",
            type=str,
            help="Path to movies.db produced by json_to_sqlite_filtered.py",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Import even when Movie table already contains data",
        )

    # ─────────────────────────────────────────────────────────
    # helpers
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def _connect(db_path: Path) -> sqlite3.Connection:
        if not db_path.exists():
            raise CommandError(f"{db_path} not found.")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _dict_iter(cur: sqlite3.Cursor, table: str, chunk: int = CHUNK) -> Iterable[Dict]:
        """
        Yield sqlite rows converted to dicts in reasonably large chunks.
        Fetching row-by-row is slow – fetchmany() is much faster.
        """
        cur.execute(f"SELECT * FROM {table}")
        while True:
            rows = cur.fetchmany(chunk)
            if not rows:
                break
            for r in rows:
                yield dict(r)

    @staticmethod
    def _bulk_insert(model, objs: List[models.Model]) -> int:
        """
        Insert list of model instances with bulk_create, clear the list,
        and return the number of rows flushed.
        """
        if not objs:
            return 0
        model.objects.bulk_create(objs, ignore_conflicts=True, batch_size=BATCH)
        n = len(objs)
        objs.clear()
        return n

    # ─────────────────────────────────────────────────────────
    # m2m helpers
    # ─────────────────────────────────────────────────────────
    def _through_info(
        self, through: models.Model
    ) -> Tuple[str, str]:
        """
        Return (movie_fk_name, other_fk_name) for the given through model.
        Assumes exactly two FK fields: one to Movie and one to the related model.
        """
        fks = [f for f in through._meta.fields if isinstance(f, models.ForeignKey)]
        movie_fk = next(f for f in fks if f.remote_field.model is Movie)
        other_fk = next(f for f in fks if f.remote_field.model is not Movie)
        return movie_fk.name, other_fk.name

    # ─────────────────────────────────────────────────────────
    # command entry-point
    # ─────────────────────────────────────────────────────────
    def handle(self, *args, **opts):
        # ─────────────────────────────────────────────────────
        # sanity check
        # ─────────────────────────────────────────────────────
        if Movie.objects.exists() and not opts["force"]:
            self.stdout.write(
                self.style.NOTICE("Movies already present – skipping import.")
            )
            return

        db_file = Path(opts["sqlite_file"]).resolve()
        self.stdout.write(f"Loading from {db_file} …")
        conn = self._connect(db_file)
        cur = conn.cursor()

        # run everything inside ONE transaction
        with transaction.atomic():
            # -------------------------------------------------
            # 1. lookup tables
            # -------------------------------------------------
            self.stdout.write("→ importing lookup tables")

            def load_lookup(sqlite_table, model_cls, mapper):
                pending: List[models.Model] = []
                inserted = 0
                total_sqlite = cur.execute(f"SELECT COUNT(*) FROM {sqlite_table}").fetchone()[
                    0
                ]
                for row in self._dict_iter(cur, sqlite_table):
                    pending.append(model_cls(**mapper(row)))
                    if len(pending) >= BATCH:
                        inserted += self._bulk_insert(model_cls, pending)
                        self._progress(model_cls.__name__, inserted, total_sqlite)
                inserted += self._bulk_insert(model_cls, pending)
                self._progress(model_cls.__name__, inserted, total_sqlite, done=True)

            load_lookup(
                "movie_genres",
                Genre,
                lambda r: {"tmdb_id": r["genre_id"], "name": r["genre_name"]},
            )
            load_lookup(
                "movie_spoken_languages",
                SpokenLanguage,
                lambda r: {
                    "iso_639_1": r["iso_639_1"],
                    "name": r["name"] or r["english_name"],
                    "english_name": r["english_name"],
                },
            )
            load_lookup(
                "movie_origin_countries",
                OriginCountry,
                lambda r: {"iso_3166_1": r["iso_3166_1"]},
            )
            load_lookup(
                "movie_production_companies",
                ProductionCompany,
                lambda r: {
                    "tmdb_id": r["company_id"],
                    "name": r["name"],
                    "origin_country": r["origin_country"],
                    "logo_path": r["logo_path"],
                },
            )
            load_lookup(
                "movie_production_countries",
                ProductionCountry,
                lambda r: {
                    "iso_3166_1": r["iso_3166_1"],
                    "name": r["name"],
                },
            )
            load_lookup(
                "movie_videos",
                Video,
                lambda r: {
                    "video_id": r["video_id"],
                    "key": r["key"],
                    "name": r["name"],
                    "site": r["site"],
                    "size": r["size"],
                    "type": r["type"],
                    "official": r["official"],
                    "published_at": r["published_at"],
                },
            )

            # -------------------------------------------------
            # 2. movies
            # -------------------------------------------------
            self.stdout.write("\n→ importing movies")
            pending: List[Movie] = []
            inserted = 0
            total_sqlite = cur.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
            for row in self._dict_iter(cur, "movies"):
                pending.append(Movie(**row))
                if len(pending) >= BATCH:
                    inserted += self._bulk_insert(Movie, pending)
                    self._progress("Movie", inserted, total_sqlite)
            inserted += self._bulk_insert(Movie, pending)
            self._progress("Movie", inserted, total_sqlite, done=True)

            # -------------------------------------------------
            # 3. through relations
            # -------------------------------------------------
            self.stdout.write("\n→ linking many-to-many relations")

            # mapping from import-name to through model
            THROUGH = {
                "genres": Movie.genres.through,
                "spoken_languages": Movie.spoken_languages.through,
                "origin_countries": Movie.origin_countries.through,
                "production_companies": Movie.production_companies.through,
                "production_countries": Movie.production_countries.through,
                "videos": Movie.videos.through,
            }

            def link(table: str, getter, field_name: str):
                through = THROUGH[field_name]
                movie_fk, other_fk = self._through_info(through)

                total = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                pending: List[models.Model] = []
                done = 0

                for rel in self._dict_iter(cur, table):
                    m_id, o_id = getter(rel)
                    pending.append(
                        through(
                            **{
                                f"{movie_fk}_id": m_id,
                                f"{other_fk}_id": o_id,
                            }
                        )
                    )
                    if len(pending) >= BATCH:
                        done += self._bulk_insert(through, pending)
                        self._progress(table, done, total)
                done += self._bulk_insert(through, pending)
                self._progress(table, done, total, done=True)

            link("movie_genres", lambda r: (r["movie_id"], r["genre_id"]), "genres")
            link(
                "movie_spoken_languages",
                lambda r: (r["movie_id"], r["iso_639_1"]),
                "spoken_languages",
            )
            link(
                "movie_origin_countries",
                lambda r: (r["movie_id"], r["iso_3166_1"]),
                "origin_countries",
            )
            link(
                "movie_production_companies",
                lambda r: (r["movie_id"], r["company_id"]),
                "production_companies",
            )
            link(
                "movie_production_countries",
                lambda r: (r["movie_id"], r["iso_3166_1"]),
                "production_countries",
            )
            link("movie_videos", lambda r: (r["movie_id"], r["video_id"]), "videos")

        self.stdout.write(self.style.SUCCESS("\nImport finished."))

    # ─────────────────────────────────────────────────────────
    # util for live status lines
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def _progress(label: str, current: int, total: int, *, done=False):
        pct = f"{100 * current / total:5.1f}%"
        end = "\n" if done else "\r"
        msg = f"{label.ljust(25)} {current:>9,}/{total:<9,}  {pct}"
        print(msg, end=end, file=sys.stdout, flush=True)
