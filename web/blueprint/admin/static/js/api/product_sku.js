function postProductsIdSkus(productId, data, silent = false) {
    const url = `/api/v1/products/${productId}/skus`;
    return callApi('POST', url, data, 'application/json', silent);
}