function postCarts(silent = false) {
    const url = `/api/v1/carts`;
    return callApi('POST', url, null, null, silent);
}

function getCarts(silent = false) {
    const url = `/api/v1/carts`;
    return callApi('GET', url, null, null, silent);
}

function patchCartsId(cartId, data, silent = false) {
    const url = `/api/v1/carts/${cartId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}

function deleteCartsId(carts, silent = false) {
    const url = `/api/v1/carts/${carts}`;
    return callApi('DELETE', url, null, null, silent);
}