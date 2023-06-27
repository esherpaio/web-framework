function postProductsIdOptions(productId, data, silent = false) {
    const url = `/api/v1/products/${productId}/options`;
    return callApi('POST', url, data, 'application/json', silent);
}

function patchProductsIdOptionsId(productId, optionId, data, silent = false) {
    const url = `/api/v1/products/${productId}/options/${optionId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}

function deleteProductsIdOptionsId(productId, optionId, silent = false) {
    const url = `/api/v1/products/${productId}/options/${optionId}`;
    return callApi('DELETE', url, null, null, silent);
}