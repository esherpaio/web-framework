function postShippings(data, silent = false) {
    const url = `/api/v1/shippings`;
    return callApi('POST', url, data, 'application/json', silent);
}

function getShippings(shippingId, silent = false) {
    const url = `/api/v1/shippings/${shippingId}`;
    return callApi('GET', url, null, null, silent);
}

function patchShippingsId(shippingsId, data, silent = false) {
    const url = `/api/v1/shippings/${shippingsId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}