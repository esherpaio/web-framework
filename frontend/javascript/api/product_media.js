function postProductsIdMedia(productId, data, silent = false) {
    const url = `/api/v1/products/${productId}/media`;
    return callApi('POST', url, data, false, silent);
}

function patchProductsIdMediaId(productId, mediaId, data, silent = false) {
    const url = `/api/v1/products/${productId}/media/${mediaId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}

function deleteProductsIdMediaId(productId, mediaId, silent = false) {
    const url = `/api/v1/products/${productId}/media/${mediaId}`;
    return callApi('DELETE', url, null, null, silent);
}