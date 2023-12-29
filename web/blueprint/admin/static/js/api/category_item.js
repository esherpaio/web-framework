function postCategoriesIdItems(categoryId, data, silent = false) {
    const url = `/api/v1/categories/${categoryId}/items`;
    return callApi('POST', url, data, 'application/json', silent);
}

function patchCategoriesIdItemsId(categoryId, itemId, data, silent = false) {
    const url = `/api/v1/categories/${categoryId}/items/${itemId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}

function deleteCategoriesIdItemsId(categoryId, itemId, silent = false) {
    const url = `/api/v1/categories/${categoryId}/items/${itemId}`;
    return callApi('DELETE', url, null, null, silent);
}