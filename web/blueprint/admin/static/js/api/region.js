function postRegions(data, silent = false) {
    const url = `/api/v1/regions`;
    return callApi('POST', url, data, 'application/json', silent);
}

function getRegions(silent = false) {
    const url = `/api/v1/regions`;
    return callApi('GET', url, null, null, silent);
}

function getRegionsId(regionId, silent = false) {
    const url = `/api/v1/regions/${regionId}`;
    return callApi('GET', url, null, null, silent);
}

function deleteRegionsId(regionId, silent = false) {
    const url = `/api/v1/regions/${regionId}`;
    return callApi('DELETE', url, null, null, silent);
}