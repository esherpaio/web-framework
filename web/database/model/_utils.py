from sqlalchemy import ForeignKey, Numeric

default_price = Numeric(10, 4, asdecimal=False)
default_vat = Numeric(4, 2, asdecimal=False)
default_rate = Numeric(10, 4, asdecimal=False)


class FKRestrict(ForeignKey):
    def __init__(self, *args, ondelete: str | None = "RESTRICT", **kwargs) -> None:
        super().__init__(*args, ondelete=ondelete, **kwargs)


class FKCascade(ForeignKey):
    def __init__(self, *args, ondelete: str | None = "CASCADE", **kwargs) -> None:
        super().__init__(*args, ondelete=ondelete, **kwargs)


class FKSetNull(ForeignKey):
    def __init__(self, *args, ondelete: str | None = "SET NULL", **kwargs) -> None:
        super().__init__(*args, ondelete=ondelete, **kwargs)
