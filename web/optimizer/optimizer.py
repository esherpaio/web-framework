from functools import cached_property, wraps
from typing import Callable

from flask import Flask, Response, g, request
from flask.typing import ResponseReturnValue

from web.logger import log
from web.setup import config
from web.utils import Singleton

from .cache import CacheKey, ResponseCache
from .compression import compress, negotiate_encoding
from .enum import CacheStatus, Encoding, G
from .minification import minification_for, minify

DEFAULT_SERVER_CACHE_MAX_MB = 32
CACHEABLE_METHODS = ("GET", "HEAD")
FORBIDDING_DIRECTIVES = ("private", "no-store", "no-cache")


class Optimizer(metaclass=Singleton):
    def __init__(self, app: Flask | None = None) -> None:
        if app is not None:
            self.init(app)

    def init(self, app: Flask) -> None:
        app.after_request(self.after_request)

    #
    # Public
    #

    def cache(
        self,
        view: Callable[..., ResponseReturnValue],
    ) -> Callable[..., ResponseReturnValue]:
        @wraps(view)
        def wrapped_view(*args, **kwargs) -> ResponseReturnValue:
            if not self._is_cacheable_request():
                return view(*args, **kwargs)
            if not request.cache_control.no_cache:
                key = self._cache_key(self._accepted_encoding())
                response = self._cache.get(key)
                if response is not None:
                    setattr(g, G.CACHE_STATUS, CacheStatus.HIT)
                    return response
            setattr(g, G.CACHE_STATUS, CacheStatus.MISS)
            return view(*args, **kwargs)

        return wrapped_view

    def after_request(self, response: Response) -> Response:
        if not self._should_optimize(response):
            return response
        encoding = self._accepted_encoding()
        cacheable = self._is_cacheable_response(response)
        self._optimize(response, encoding)
        self._set_headers(response, encoding, cacheable)
        if self._cache_status() is CacheStatus.MISS:
            self._store(response, encoding, cacheable)
        return response

    def del_cache(self) -> None:
        if self._cache.clear():
            log.warning("Optimizer cache cleared")

    #
    # Pipeline
    #

    def _should_optimize(self, response: Response) -> bool:
        return (
            self._is_active_for(request.path)
            and self._cache_status() is not CacheStatus.HIT
            and not response.direct_passthrough
            and not response.is_streamed
            and response.content_length is not None
            and 200 <= response.status_code < 300
            and "Content-Encoding" not in response.headers
        )

    @staticmethod
    def _optimize(response: Response, encoding: Encoding | None) -> None:
        minification = minification_for(response.mimetype)
        if minification is not None:
            response.set_data(minify(response.get_data(as_text=True), minification))
            log.debug(f"Optimizer minified {request.full_path}")
        if encoding is not None:
            response.set_data(compress(response.get_data(), encoding))
            log.debug(f"Optimizer compressed {request.full_path}")

    @staticmethod
    def _set_headers(
        response: Response,
        encoding: Encoding | None,
        cacheable: bool,
    ) -> None:
        if cacheable and "Cache-Control" not in response.headers:
            response.headers["Cache-Control"] = (
                "public, "
                f"max-age={config.OPTIMIZER_BROWSER_CACHE_MAX_S}, "
                f"s-maxage={config.OPTIMIZER_CDN_CACHE_MAX_S}, "
                f"stale-while-revalidate={config.OPTIMIZER_CDN_STALE_MAX_S}"
            )
        if encoding is not None:
            response.headers["Content-Encoding"] = encoding
        response.vary.add("Accept-Encoding")

    def _store(
        self,
        response: Response,
        encoding: Encoding | None,
        cacheable: bool,
    ) -> None:
        key = self._cache_key(encoding)
        if cacheable:
            if self._cache.set(key, response):
                log.info(f"Optimizer cached {request.full_path}")
        elif self._forbids_caching(response):
            self._cache.delete(key)

    #
    # Cache policy
    #

    @staticmethod
    def _is_active_for(path: str) -> bool:
        ignore_paths: list[str] = config.OPTIMIZER_IGNORE_PATHS or []
        return config.OPTIMIZER_ENABLED and not path.startswith(tuple(ignore_paths))

    def _is_cacheable_request(self) -> bool:
        return (
            self._is_active_for(request.path)
            and request.method in CACHEABLE_METHODS
            and self._is_canonical_host()
            and not request.cache_control.no_store
        )

    def _is_cacheable_response(self, response: Response) -> bool:
        return (
            self._cache_status() is CacheStatus.MISS
            and response.status_code == 200
            and not self._forbids_caching(response)
            and "Set-Cookie" not in response.headers
            and response.vary.as_set() <= {"accept-encoding"}
        )

    @staticmethod
    def _forbids_caching(response: Response) -> bool:
        return any(x in response.cache_control for x in FORBIDDING_DIRECTIVES)

    @staticmethod
    def _is_canonical_host() -> bool:
        if config.DEBUG:
            return True
        host = request.host.split(":", 1)[0].removeprefix("www.")
        return host == config.DOMAIN_NAME

    #
    # Cache access
    #

    @cached_property
    def _cache(self) -> ResponseCache:
        max_mb = config.OPTIMIZER_SERVER_CACHE_MAX_MB
        if max_mb is None:
            max_mb = DEFAULT_SERVER_CACHE_MAX_MB
        return ResponseCache(
            max_age_s=config.OPTIMIZER_SERVER_CACHE_MAX_S,
            max_bytes=max_mb * 1024 * 1024,
        )

    @staticmethod
    def _cache_status() -> CacheStatus | None:
        return g.get(G.CACHE_STATUS)

    @staticmethod
    def _cache_key(encoding: Encoding | None) -> CacheKey:
        return CacheKey(request.full_path, encoding)

    @staticmethod
    def _accepted_encoding() -> Encoding | None:
        return negotiate_encoding(request.headers.get("Accept-Encoding", ""))


optimizer = Optimizer()
