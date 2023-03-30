from webshop.database.model import Currency, CurrencyId

currency_seeds = [
    Currency(id=CurrencyId.EUR, code="EUR", symbol="€"),
    Currency(id=CurrencyId.USD, code="USD", symbol="$"),
]
