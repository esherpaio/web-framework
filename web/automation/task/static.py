import io
import os
from collections import defaultdict
from datetime import datetime
from enum import StrEnum
from typing import Type

from sqlalchemy.orm import Session

from web import cdn
from web.database import conn
from web.database.model import AppBlueprint, AppRoute, AppSettings
from web.logger import log
from web.packer import Packer
from web.packer.bundle import CssBundle, JsBundle, ScssBundle
from web.setup import config

from ..automator import Processor

if not config.DEBUG:
    STATIC_DIR = "static"
else:
    STATIC_DIR = "cdn"


class StaticType(StrEnum):
    JS = "js"
    CSS = "css"


class StaticJob:
    def __init__(
        self,
        type_: StaticType,
        bundles: list[JsBundle | ScssBundle | CssBundle],
        model: Type[AppSettings | AppBlueprint | AppRoute],
        endpoint: str = "",
    ) -> None:
        self.type_: StaticType = type_
        self.bundles: list[JsBundle | ScssBundle | CssBundle] = bundles
        self.model: Type[AppSettings | AppBlueprint | AppRoute] = model
        self.endpoint: str = endpoint

    @property
    def id_(self) -> str:
        parts = [self.model.__tablename__, self.type_]
        if self.endpoint:
            parts.append(self.endpoint)
        return ":".join(parts)

    def get_resource(
        self,
        s: Session,
    ) -> AppSettings | AppBlueprint | AppRoute | None:
        if self.model == AppSettings:
            return s.query(AppSettings).first()
        elif self.model == AppBlueprint:
            return s.query(AppBlueprint).filter_by(endpoint=self.endpoint).first()
        elif self.model == AppRoute:
            return s.query(AppRoute).filter_by(endpoint=self.endpoint).first()
        log.error(f"Static job model {self.model} is unsupported")
        return None

    def set_attribute(
        self,
        s: Session,
        resource: AppSettings | AppBlueprint | AppRoute,
        cdn_path: str,
    ) -> None:
        if self.type_ is StaticType.JS:
            resource.js_path = cdn_path
        elif self.type_ is StaticType.CSS:
            resource.css_path = cdn_path
        else:
            log.error(f"Static job type {self.type_} is unsupported")


class StaticProcessor(Processor):
    JOBS: list[StaticJob]
    KEEP: int = 50

    def __init__(self, *args, **kwargs) -> None:
        if not config.DEBUG:
            self.REQUIRES_APP = False
        else:
            self.REQUIRES_APP = True

    @classmethod
    def run(cls) -> None:
        cls.log_start()
        if not config.AUTOMATE_STATIC:
            log.warning("Static processor is disabled")
            return
        with cdn.connect() as client:
            modified = client.modified(os.path.join(STATIC_DIR))
            with conn.begin() as s:
                resources = cls.load_resources(s)
                uploaded = cls.upload_bundles(s, client, resources, set(modified))
                s.flush()
            with conn.begin() as s:
                cls.clear_stale_paths(s, uploaded)
            with conn.begin() as s:
                cls.prune_files(s, client, modified)

    @classmethod
    def load_resources(
        cls,
        s: Session,
    ) -> dict[StaticJob, AppSettings | AppBlueprint | AppRoute]:
        resources: dict[StaticJob, AppSettings | AppBlueprint | AppRoute] = {}
        for job in cls.JOBS:
            resource = job.get_resource(s)
            if resource is None:
                log.error(f"Static job {job.id_} resource is not found")
                continue
            resources[job] = resource
        return resources

    @classmethod
    def upload_bundles(
        cls,
        s: Session,
        client: cdn.BaseClient,
        resources: dict[StaticJob, AppSettings | AppBlueprint | AppRoute],
        cdn_filenames: set[str],
    ) -> dict[tuple[str, int], list[StaticType]]:
        processed: dict[tuple[str, int], list[StaticType]] = defaultdict(list)
        for job in cls.JOBS:
            resource = resources[job]
            packer = Packer()
            out_ext = packer.validate(job.bundles)
            compiled, bytes_, hash_ = packer.pack(job.bundles)
            if not compiled:
                log.error(f"Static job {job.id_} compiled empty")
                continue
            cdn_filename = f"{hash_}{out_ext}"
            cdn_path = os.path.join(STATIC_DIR, cdn_filename)
            if cdn_filename not in cdn_filenames:
                client.upload(io.BytesIO(bytes_), cdn_path)
            job.set_attribute(s, resource, cdn_path)
            processed[(resource.__tablename__, resource.id)].append(job.type_)
        return processed

    @classmethod
    def clear_stale_paths(
        cls,
        s: Session,
        present: dict[tuple[str, int], list[StaticType]],
    ) -> None:
        for resource in [
            *s.query(AppSettings).all(),
            *s.query(AppBlueprint).all(),
            *s.query(AppRoute).all(),
        ]:
            present_types = present[(resource.__tablename__, resource.id)]
            absent_types = [t for t in list(StaticType) if t not in present_types]
            for type_ in absent_types:
                if type_ == StaticType.JS and resource.js_path:  # type: ignore[attr-defined]
                    resource.js_path = None  # type: ignore[attr-defined]
                elif type_ == StaticType.CSS and resource.css_path:  # type: ignore[attr-defined]
                    resource.css_path = None  # type: ignore[attr-defined]
                s.flush()

    @classmethod
    def prune_files(
        cls,
        s: Session,
        client: cdn.BaseClient,
        modified: dict[str, datetime],
    ) -> None:
        active: set[str] = set()
        for resource in [
            *s.query(AppSettings).all(),
            *s.query(AppBlueprint).all(),
            *s.query(AppRoute).all(),
        ]:
            for path in (resource.js_path, resource.css_path):  # type: ignore[attr-defined]
                if path:
                    active.add(os.path.basename(path))
        ordered = sorted(modified, key=lambda fn: modified[fn], reverse=True)
        keep = set(ordered[: cls.KEEP]) | active
        for fn in ordered:
            if fn not in keep:
                client.delete(os.path.join(STATIC_DIR, fn))
