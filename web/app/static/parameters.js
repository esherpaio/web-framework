function getParameter(key) {
    let url = new URL(window.location.href);
    return url.searchParams.get(key);
}

function removeParameter(key) {
    let url = new URL(window.location.href);
    url.searchParams.delete(key);
    window.history.replaceState(null, null, url);
}

function setParameter(key, value) {
    let url = new URL(window.location.href);
    url.searchParams.set(key, value);
    window.history.replaceState(null, null, url);
}
