from enum import StrEnum

from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import AppBlueprint, AppRoute, AppSetting
from web.packer.base import CssBundle, JsBundle, Packer, ScssBundle
from web.seeder.abc import Syncer


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
            resource.js_path = cdn_path
        elif self.type == StaticType.CSS:
            resource.css_path = cdn_path
        s.flush()


class StaticSyncer(Syncer):
    def __init__(self, seeds: list[StaticSeed]) -> None:
        super().__init__()
        self.seeds: list[StaticSeed] = seeds

    def sync(self, s: Session) -> None:
        for seed in self.seeds:
            with conn.begin() as s:
                resource = seed.get_resource(s)
                if resource is not None:
                    seed.set_attribute(s, resource)
