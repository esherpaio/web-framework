import urllib.parse


def strip_scheme(url: str) -> str:
    url_parsed = urllib.parse.urlparse(url)
    scheme = f"{url_parsed.scheme}://"
    return url_parsed.geturl().replace(scheme, "", 1)


def replace_domain(in_url: str, new_domain: str) -> str:
    new_domain = strip_scheme(new_domain)
    in_url_parsed = urllib.parse.urlparse(in_url)
    new_url_parsed = in_url_parsed._replace(netloc=new_domain)
    return urllib.parse.urlunparse(new_url_parsed)
