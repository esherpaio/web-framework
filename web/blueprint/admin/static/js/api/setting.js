function getSetting(silent = false) {
    const url = `/api/v1/setting`;
    return callApi('GET', url, null, null, silent);
}

function patchSetting(data, silent = false) {
    const url = `/api/v1/setting`;
    return callApi('PATCH', url, data, 'application/json', silent);
}