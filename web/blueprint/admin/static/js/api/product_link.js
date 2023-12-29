function postProductsIdLinks(productId, data, silent = false) {
    const url = `/api/v1/products/${productId}/links`;
    return callApi('POST', url, data, 'application/json', silent);
}

function deleteProductsIdLinksId(productId, linkId, silent = false) {
    const url = `/api/v1/products/${productId}/links/${linkId}`;
    return callApi('DELETE', url, null, null, silent);
}