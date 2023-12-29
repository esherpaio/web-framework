function postProducts(data, silent = false) {
    const url = `/api/v1/products`;
    return callApi('POST', url, data, 'application/json', silent);
}

function patchProductsId(productId, data, silent = false) {
    const url = `/api/v1/products/${productId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}

function deleteProductsId(productId, silent = false) {
    const url = `/api/v1/products/${productId}`;
    return callApi('DELETE', url, null, null, silent);
}