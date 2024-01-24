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

    def set_attribute(self, s: Session) -> None:
        # upload bundle to cdn
        _, cdn_path = Packer().pack(self.bundle, save_cdn=True)
        # get resource
        obj: AppSetting | AppBlueprint | AppRoute | None
        if self.model == AppSetting:
            obj = s.query(AppSetting).first()
        elif self.model == AppBlueprint:
            obj = s.query(AppBlueprint).filter_by(endpoint=self.endpoint).first()
        elif self.model == AppRoute:
            obj = s.query(AppRoute).filter_by(endpoint=self.endpoint).first()
        else:
            raise ValueError
        # write resource
        if obj is not None:
            if self.type == StaticType.JS:
                obj.js_path = cdn_path
            elif self.type == StaticType.CSS:
                obj.css_path = cdn_path
        s.flush()


class StaticSyncer(Syncer):
    def __init__(self, seeds: list[StaticSeed]) -> None:
        super().__init__()
        self.seeds: list[StaticSeed] = seeds

    def sync(self, s: Session) -> None:
        for seed in self.seeds:
            with conn.begin() as s:
                seed.set_attribute(s)
