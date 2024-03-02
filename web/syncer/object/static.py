from enum import StrEnum

from sqlalchemy.orm import Session

from web.config import config
from web.database import conn
from web.database.model import AppBlueprint, AppRoute, AppSetting
from web.libs.logger import log
from web.packer import Packer
from web.packer.bundle import CssBundle, JsBundle, ScssBundle
from web.syncer import Syncer


class StaticType(StrEnum):
    JS = "js"
    CSS = "css"


class StaticSeed:
    def __init__(
        self,
        type_: StaticType,
        bundle: JsBundle | ScssBundle | CssBundle,
        model: AppSetting | AppBlueprint | AppRoute,
        endpoint: str = "",
    ) -> None:
        self.type: StaticType = type_
        self.bundle: JsBundle | ScssBundle | CssBundle = bundle
        self.model: AppSetting | AppBlueprint | AppRoute = model
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
        _, cdn_path = Packer().pack(self.bundle, save_cdn=True)
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
    def sync(cls, s: Session) -> None:
        if not config.APP_STATIC:
            log.warning("Static syncer is disabled")
            return
        for seed in cls.SEEDS:
            with conn.begin() as s:
                resource = seed.get_resource(s)
                if resource is not None:
                    seed.set_attribute(s, resource)
                else:
                    log.error(
                        f"Static resource for {seed.type}:{seed.endpoint} is not found"
                    )
