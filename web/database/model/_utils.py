from sqlalchemy import JSON, Numeric
from sqlalchemy.ext.mutable import MutableDict

default_price = Numeric(10, 4, asdecimal=False)
default_vat = Numeric(4, 2, asdecimal=False)
default_rate = Numeric(10, 4, asdecimal=False)
type_json = MutableDict.as_mutable(JSON)  # type: ignore
