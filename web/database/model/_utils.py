from sqlalchemy import ForeignKey, Numeric, func

current_time = func.now()
price = Numeric(10, 4, asdecimal=False)
vat = Numeric(4, 2, asdecimal=False)
rate = Numeric(10, 4, asdecimal=False)


class FKRestrict(ForeignKey):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, ondelete="RESTRICT", **kwargs)


class FKCascade(ForeignKey):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, ondelete="CASCADE", **kwargs)


class FKSetNull(ForeignKey):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, ondelete="SET NULL", **kwargs)
