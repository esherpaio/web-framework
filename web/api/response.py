import json
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum

from werkzeug import Response

from web.i18n import _


class HttpText(StrEnum):
    HTTP_200 = _("API_HTTP_200")
    HTTP_202 = _("API_HTTP_202")
    HTTP_204 = _("API_HTTP_204")
    HTTP_400 = _("API_HTTP_400")
    HTTP_401 = _("API_HTTP_401")
    HTTP_403 = _("API_HTTP_403")
    HTTP_404 = _("API_HTTP_404")
    HTTP_409 = _("API_HTTP_409")
    HTTP_410 = _("API_HTTP_410")
    HTTP_500 = _("API_HTTP_500")


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            quantized = obj.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            return str(quantized)
        return super().default(obj)


def json_response(
    code: int = 200,
    message: str | StrEnum | None = None,
    data: list | dict | None = None,
    links: dict | None = None,
) -> Response:
    """Create a default API response."""
    if message is None:
        message = HttpText.HTTP_200
    if data is None:
        data = {}
    if links is None:
        links = {}
    value = json.dumps(
        {"code": code, "message": message, "data": data, "links": links},
        cls=JsonEncoder,
    )
    return Response(value, status=code, mimetype="application/json")
