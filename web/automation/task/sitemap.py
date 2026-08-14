import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from web.database import conn
from web.database.model import AppRoute, SitemapLocation
from web.logger import log
from web.setup import config

from ..automator import Processor


@dataclass(frozen=True)
class SitemapLocationSpec:
    """Desired sitemap state before it is reconciled with a stored location."""

    endpoint_args: dict[str, Any] = field(default_factory=dict)
    content_lastmod: datetime | None = None
    template_hash: str | None = None


def get_template_hash(
    template_path: str | Path,
    template_dir: str | Path = "templates",
) -> str | None:
    """Hash a template path relative to its application's templates directory."""
    template_file = Path(config.BASE_DIR) / template_dir / template_path
    if not template_file.exists():
        log.warning(f"Template not found: {template_file}")
        return None
    return hashlib.sha256(template_file.read_bytes()).hexdigest()


class SitemapLocationSyncer(Processor):
    """Task that maintains sitemap locations for ordinary application routes.

    The default task handles every non-collection route. Applications should use
    a separate task for collection routes whose locations come from custom queries.
    """

    INTERVAL_S = 86400
    TEMPLATE_DIR: str | Path = "templates"

    @classmethod
    def run(cls) -> None:
        cls.log_start()
        with conn.begin() as s:
            cls.sync_routes(s)

    @classmethod
    def sync_routes(cls, s: Session) -> None:
        """Synchronize every non-collection route using its stored metadata."""
        routes = s.query(AppRoute).filter_by(is_collection=False).all()
        for route in routes:
            if not route.in_sitemap:
                cls.sync(s, route.id, [])
                continue

            if route.template_path:
                template_hash = get_template_hash(
                    route.template_path,
                    cls.TEMPLATE_DIR,
                )
                spec = SitemapLocationSpec(template_hash=template_hash)
            else:
                lastmod = max(
                    (date for date in (route.created_at, route.updated_at) if date),
                    default=None,
                )
                spec = SitemapLocationSpec(content_lastmod=lastmod)
            cls.sync(s, route.id, [spec])

    @classmethod
    def sync(
        cls,
        s: Session,
        route_id: int,
        specs: list[SitemapLocationSpec],
    ) -> None:
        """Reconcile one route with the complete list of desired locations."""
        # Match locations by their endpoint arguments, such as {"slug": "about"}.
        existing = {
            cls._key(location.endpoint_args): location
            for location in s.query(SitemapLocation).filter_by(route_id=route_id).all()
        }
        desired_keys: set[str] = set()
        now = datetime.now(UTC)

        for spec in specs:
            key = cls._key(spec.endpoint_args)
            # Duplicate endpoint arguments would describe the same sitemap URL.
            if key in desired_keys:
                raise ValueError(
                    f"Duplicate sitemap location arguments for route {route_id}: "
                    f"{spec.endpoint_args}"
                )
            desired_keys.add(key)

            location = existing.get(key)
            if location is None:
                # A new page starts at its content date, or now when it has no
                # independent content timestamp.
                location = SitemapLocation(
                    route_id=route_id,
                    endpoint_args=spec.endpoint_args,
                    lastmod=spec.content_lastmod or now,
                    template_hash=spec.template_hash,
                )
                s.add(location)
                continue

            # Content dates only move forward. Older source timestamps must not
            # make a previously published lastmod go backwards.
            if (
                spec.content_lastmod is not None
                and spec.content_lastmod > location.lastmod
            ):
                location.lastmod = spec.content_lastmod
            # A changed template means the rendered page changed today, even if
            # the underlying content record did not change.
            if (
                spec.template_hash is not None
                and spec.template_hash != location.template_hash
            ):
                location.lastmod = max(location.lastmod, now)
            if spec.template_hash is not None:
                location.template_hash = spec.template_hash

        # The supplied specs are authoritative, so remove pages that disappeared
        # from the source query (for example deleted or hidden content).
        for key, location in existing.items():
            if key not in desired_keys:
                s.delete(location)

    @staticmethod
    def _key(endpoint_args: dict[str, Any]) -> str:
        return json.dumps(endpoint_args, sort_keys=True, separators=(",", ":"))
