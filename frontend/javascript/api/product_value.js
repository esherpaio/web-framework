function postProductsIdValues(productId, data, silent = false) {
    const url = `/api/v1/products/${productId}/values`;
    return callApi('POST', url, data, 'application/json', silent);
}

function patchProductsIdValuesId(productId, valueId, data, silent = false) {
    const url = `/api/v1/products/${productId}/values/${valueId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}

function deleteProductsIdValuesId(productId, valueId, silent = false) {
    const url = `/api/v1/products/${productId}/values/${valueId}`;
    return callApi('DELETE', url, null, null, silent);
}