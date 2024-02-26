import time

from requests import Response, Session
from slumber import API, Resource

from web.libs.logger import log


class _Session(Session):
    """Wrapper for request session."""

    def request(self, method, url, *args, **kwargs) -> Response:
        start = time.time()
        resp = super().request(method, url, *args, **kwargs)
        duration = int(1000 * (time.time() - start))
        message = f"[API] {method} {url} {resp.status_code} {duration}ms"
        if 200 <= resp.status_code <= 399:
            func = log.info
        elif 400 <= resp.status_code <= 499:
            func = log.warning
        else:
            func = log.error
        func(message)
        return resp


class _Resource(Resource):
    """Wrapper for API resource."""

    def _request(self, method, data=None, files=None, params=None):
        serializer = self._store["serializer"]
        url = self.url()
        headers = {"accept": serializer.get_content_type()}
        if not files:
            headers["content-type"] = serializer.get_content_type()
            if data is not None:
                data = serializer.dumps(data)
        resp = self._store["session"].request(
            method, url, data=data, params=params, files=files, headers=headers
        )
        self._ = resp
        return resp

    def url(self):
        url = super().url()
        if "___" in url:
            url = url.replace("___", "-")
        return url


class Client(API):
    """Wrapper for API client."""

    resource_class = _Resource

    def __init__(self, base_url: str, api_key: str | None = None):
        session = _Session()
        super().__init__(base_url, session=session, append_slash=False)
        if api_key is not None:
            self._store["session"].auth = None
            self._store["session"].headers["Authorization"] = f"Bearer {api_key}"
        self.await_connection()

    def _get_resource(self, **kwargs) -> Resource:
        if "___" in kwargs.get("base_url", ""):
            kwargs["base_url"] = kwargs["base_url"].replace("___", "-")
        return super()._get_resource(**kwargs)

    def await_connection(self) -> None:
        while True:
            try:
                self.__getattr__("").get()
                break
            except Exception:
                log.warning("[API] Connection failed")
                time.sleep(5)
        log.info("[API] Connected established")
