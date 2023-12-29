function postLanguages(data, silent = false) {
    const url = `/api/v1/languages`;
    return callApi('POST', url, data, 'application/json', silent);
}

function getLanguages(silent = false) {
    const url = `/api/v1/languages`;
    return callApi('GET', url, null, null, silent);
}

function getLanguagesId(languageId, silent = false) {
    const url = `/api/v1/languages/${languageId}`;
    return callApi('GET', url, null, null, silent);
}

function deleteLanguagesId(languageId, silent = false) {
    const url = `/api/v1/languages/${languageId}`;
    return callApi('DELETE', url, null, null, silent);
}