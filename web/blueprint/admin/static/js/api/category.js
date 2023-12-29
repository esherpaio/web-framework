function postCategories(data, silent = false) {
    const url = `/api/v1/categories`;
    return callApi('POST', url, data, 'application/json', silent);
}

function patchCategories(categoryId, data, silent = false) {
    const url = `/api/v1/categories/${categoryId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}

function deleteCategoriesId(categoryId, silent = false) {
    const url = `/api/v1/categories/${categoryId}`;
    return callApi('DELETE', url, null, null, silent);
}