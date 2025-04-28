import os
from collections import defaultdict
from enum import StrEnum
from typing import Type

from sqlalchemy.orm import Session

from web import cdn
from web.config import config
from web.database import conn
from web.database.model import AppBlueprint, AppRoute, AppSettings
from web.logger import log
from web.packer import Packer
from web.packer.bundle import CssBundle, JsBundle, ScssBundle

from ..automator import Processor


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
        if self.model == AppBlueprint:
            return s.query(AppBlueprint).filter_by(endpoint=self.endpoint).first()
        if self.model == AppRoute:
            return s.query(AppRoute).filter_by(endpoint=self.endpoint).first()
        log.error(f"Static job model {self.model} is unsupported")
        return None

    def set_attribute(
        self,
        s: Session,
        resource: AppSettings | AppBlueprint | AppRoute,
        cdn_path: str,
    ) -> None:
        if self.type_ == StaticType.JS:
            resource.js_path = cdn_path
            s.flush()
            return
        if self.type_ == StaticType.CSS:
            resource.css_path = cdn_path
            s.flush()
            return
        log.error(f"Static job type {self.type_} is unsupported")
        return


class StaticProcessor(Processor):
    JOBS: list[StaticJob]

    @classmethod
    def run(cls) -> None:
        log.info("1")
        cls.log_start()
        log.info("2")
        if not config.APP_SYNC_STATIC:
            log.warning("Static processor is disabled")
            return
        log.info("3")
        with conn.begin() as s:
            resources = cls.get_resources(s)
            log.info("4")
            log.info(f"{resources}")
            cdn_filenames = cdn.filenames(os.path.join("static", ""))
            log.info("5")
            log.info(f"{cdn_filenames}")
            present = cls.set_resources(s, resources, cdn_filenames)
            log.info("6")
            log.info(present)
        with conn.begin() as s:
            cls.del_resources(s, present)
        log.info(f"7")

    @classmethod
    def get_resources(
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
    def set_resources(
        cls,
        s: Session,
        resources: dict[StaticJob, AppSettings | AppBlueprint | AppRoute],
        cdn_filenames: list[str],
    ) -> dict[tuple[str, int], list[StaticType]]:
        present: dict[tuple[str, int], list[StaticType]] = defaultdict(list)
        for job in cls.JOBS:
            resource = resources[job]
            packer = Packer()
            out_ext = packer.validate(job.bundles)
            compiled, bytes_, hash_ = packer.pack(job.bundles)
            if not compiled:
                log.error(f"Static job {job.id_} compiled empty")
                continue
            present[(resource.__tablename__, resource.id)].append(job.type_)
            cdn_filename = f"{hash_}{out_ext}"
            cdn_path = os.path.join("static", cdn_filename)
            if cdn_filename not in cdn_filenames:
                packer.write_cdn(bytes_, cdn_path)
            job.set_attribute(s, resource, cdn_path)
        return present

    @classmethod
    def del_resources(
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
            for absent_type in absent_types:
                if absent_type == StaticType.JS and resource.js_path:  # type: ignore[attr-defined]
                    resource.js_path = None  # type: ignore[attr-defined]
                elif absent_type == StaticType.CSS and resource.css_path:  # type: ignore[attr-defined]
                    resource.css_path = None  # type: ignore[attr-defined]
                s.flush()
