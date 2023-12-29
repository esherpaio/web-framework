function postSessions(data, silent = false) {
    const url = `/api/v1/sessions`;
    return callApi('POST', url, data, 'application/json', silent);
}

function deleteSessions(silent = false) {
    const url = `/api/v1/sessions`;
    return callApi('DELETE', url, null, 'application/json', silent);
}