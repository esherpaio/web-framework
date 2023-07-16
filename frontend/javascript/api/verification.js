function getVerifications(data, silent = false) {
    const url = `/api/v1/verifications`;
    return callApi('GET', url, data, null, silent);
}