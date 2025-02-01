import os
from collections import defaultdict
from enum import StrEnum
from typing import Type

from sqlalchemy.orm import Session

from web import cdn
from web.config import config
from web.database import conn
from web.database.model import AppBlueprint, AppRoute, AppSetting
from web.logger import log
from web.packer import Packer
from web.packer.bundle import CssBundle, JsBundle, ScssBundle

from ..syncer import Syncer


class StaticType(StrEnum):
    JS = "js"
    CSS = "css"


class StaticSeed:
    def __init__(
        self,
        type_: StaticType,
        bundles: list[JsBundle | ScssBundle | CssBundle],
        model: Type[AppSetting | AppBlueprint | AppRoute],
        endpoint: str = "",
    ) -> None:
        self.type: StaticType = type_
        self.bundles: list[JsBundle | ScssBundle | CssBundle] = bundles
        self.model: Type[AppSetting | AppBlueprint | AppRoute] = model
        self.endpoint: str = endpoint

    @property
    def id_(self) -> str:
        return f"{self.model.__tablename__}:{self.type}"

    def get_resource(
        self,
        s: Session,
    ) -> AppSetting | AppBlueprint | AppRoute | None:
        obj: AppSetting | AppBlueprint | AppRoute | None
        if self.model == AppSetting:
            obj = s.query(AppSetting).first()
        elif self.model == AppBlueprint:
            obj = s.query(AppBlueprint).filter_by(endpoint=self.endpoint).first()
        elif self.model == AppRoute:
            obj = s.query(AppRoute).filter_by(endpoint=self.endpoint).first()
        return obj

    def set_attribute(
        self,
        s: Session,
        resource: AppSetting | AppBlueprint | AppRoute,
        cdn_path: str,
    ) -> None:
        if self.type == StaticType.JS and resource.js_path != cdn_path:
            resource.js_path = cdn_path
            s.flush()
        elif self.type == StaticType.CSS and resource.css_path != cdn_path:
            resource.css_path = cdn_path
            s.flush()
        else:
            log.error(f"Static seed type {self.type} unsupported")


class StaticSyncer(Syncer):
    SEEDS: list[StaticSeed]

    @classmethod
    def run(cls, s: Session) -> None:
        if not config.APP_SYNC_STATIC:
            log.warning("Static syncer is disabled")
            return
        resources = cls.get_resources()
        cdn_filenames = cdn.filenames(os.path.join("static", ""))
        present = cls.set_resources(resources, cdn_filenames)
        cls.remove_unused(present)

    @classmethod
    def get_resources(
        cls,
    ) -> dict[StaticSeed, AppSetting | AppBlueprint | AppRoute]:
        resources: dict[StaticSeed, AppSetting | AppBlueprint | AppRoute] = {}
        with conn.begin() as s:
            for seed in cls.SEEDS:
                resource = seed.get_resource(s)
                if resource is None:
                    log.error(f"Static resource {seed.id_} is not found")
                    continue
                resources[seed] = resource
        return resources

    @classmethod
    def set_resources(
        cls,
        resources: dict[StaticSeed, AppSetting | AppBlueprint | AppRoute],
        cdn_filenames: list[str],
    ) -> dict[tuple[str, int], list[StaticType]]:
        present: dict[tuple[str, int], list[StaticType]] = defaultdict(list)
        for seed in cls.SEEDS:
            resource = resources[seed]
            packer = Packer()
            out_ext = packer.validate(seed.bundles)
            compiled, bytes_, hash_ = packer.pack(seed.bundles)
            if not compiled:
                log.error(f"Static resource {seed.id_} empty result")
                continue
            present[(resource.__tablename__, resource.id)].append(seed.type)
            cdn_filename = f"{hash_}{out_ext}"
            if cdn_filename in cdn_filenames:
                log.info(f"Static resource {seed.id_} already exists")
                continue
            cdn_path = os.path.join("static", cdn_filename)
            packer.write_cdn(bytes_, cdn_path)
            with conn.begin() as s:
                seed.set_attribute(s, resource, cdn_path)
        return present

    @classmethod
    def remove_unused(
        cls,
        present: dict[tuple[str, int], list[StaticType]],
    ) -> None:
        with conn.begin() as s:
            for resource in [
                *s.query(AppSetting).all(),
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
