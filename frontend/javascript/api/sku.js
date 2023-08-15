function patchSkusId(skuId, data, silent = false) {
    const url = `/api/v1/skus/${skuId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}

function deleteSkusId(skuId, silent = false) {
    const url = `/api/v1/skus/${skuId}`;
    return callApi('DELETE', url, null, null, silent);
}