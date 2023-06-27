function postCartsIdItems(cartId, data, silent = false) {
    const url = `/api/v1/carts/${cartId}/items`;
    return callApi('POST', url, data, 'application/json', silent);
}

function patchCartIdItemsId(cartId, cartItemId, data, silent = false) {
    const url = `/api/v1/carts/${cartId}/items/${cartItemId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}

function deleteCartIdItemsId(cartId, cartItemId, silent = false) {
    const url = `/api/v1/carts/${cartId}/items/${cartItemId}`;
    return callApi('DELETE', url, null, null, silent);
}