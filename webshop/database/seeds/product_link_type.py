from webshop.database.model import ProductLinkType, ProductLinkTypeId

product_link_type_seeds = [
    ProductLinkType(id=ProductLinkTypeId.CROSS_SELL, name="Cross-sell"),
    ProductLinkType(id=ProductLinkTypeId.UPSELL, name="Upsell"),
]
