from web.database.client import conn
from web.seeder.model import (
    CountrySyncer,
    CurrencySyncer,
    FileTypeSyncer,
    OrderStatusSyncer,
    ProductLinkeTypeSyncer,
    ProductTypeSyncer,
    RegionSyncer,
    SkuSyncer,
    UserRoleSyncer,
)


def run_seeders() -> None:
    with conn.begin() as s:
        # Locale
        CountrySyncer().sync(s)
        RegionSyncer().sync(s)
        CurrencySyncer().sync(s)
        # Types
        FileTypeSyncer().sync(s)
        OrderStatusSyncer().sync(s)
        ProductLinkeTypeSyncer().sync(s)
        ProductTypeSyncer().sync(s)
        UserRoleSyncer().sync(s)
        # Data
        SkuSyncer().sync(s)
