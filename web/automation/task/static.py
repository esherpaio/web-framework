from collections import defaultdict
from enum import StrEnum
from typing import Type

from sqlalchemy.orm import Session

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

    def get_resource(self, s: Session) -> AppSetting | AppBlueprint | AppRoute | None:
        obj: AppSetting | AppBlueprint | AppRoute | None
        if self.model == AppSetting:
            obj = s.query(AppSetting).first()
        elif self.model == AppBlueprint:
            obj = s.query(AppBlueprint).filter_by(endpoint=self.endpoint).first()
        elif self.model == AppRoute:
            obj = s.query(AppRoute).filter_by(endpoint=self.endpoint).first()
        return obj

    def set_attribute(
        self, s: Session, resource: AppSetting | AppBlueprint | AppRoute
    ) -> None:
        # upload bundle to cdn
        _, cdn_path = Packer().pack(self.bundles, save_cdn=True)
        # write resource
        if self.type == StaticType.JS:
            if resource.js_path != cdn_path:
                resource.js_path = cdn_path
                s.flush()
        elif self.type == StaticType.CSS:
            if resource.css_path != cdn_path:
                resource.css_path = cdn_path
                s.flush()


class StaticSyncer(Syncer):
    @classmethod
    def run(cls, s: Session) -> None:
        if not config.APP_SYNC_STATIC:
            log.warning("Static syncer is disabled")
            return

        # TODO(Stan): Doing `cdn.exists` for each bundle is expensive. Optimize
        #  by fetching all filenames first, then generate all hashes, and
        #  filter in Python.

        # Update static resources
        synced = defaultdict(list)
        for seed in cls.SEEDS:
            with conn.begin() as s:
                resource = seed.get_resource(s)
                if resource is not None:
                    seed.set_attribute(s, resource)
                    synced[(resource.__table__.name, resource.id)].append(seed.type)
                else:
                    log.error(
                        f"Static resource for {seed.type}:{seed.endpoint} is not found"
                    )

        # Remove unused static resources
        with conn.begin() as s:
            for check in [
                *s.query(AppSetting).all(),
                *s.query(AppBlueprint).all(),
                *s.query(AppRoute).all(),
            ]:
                synced_types = synced[(check.__table__.name, check.id)]  # type: ignore[attr-defined]
                unsynced_types = [s for s in list(StaticType) if s not in synced_types]
                for unsynced in unsynced_types:
                    if unsynced == StaticType.JS and check.js_path:  # type: ignore[attr-defined]
                        check.js_path = None  # type: ignore[attr-defined]
                    elif unsynced == StaticType.CSS and check.css_path:  # type: ignore[attr-defined]
                        check.css_path = None  # type: ignore[attr-defined]
                    s.flush()
