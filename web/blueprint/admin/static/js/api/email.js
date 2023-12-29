function postEmails(data, silent = false) {
    const url = `/api/v1/emails`;
    return callApi('POST', url, data, 'application/json', silent);
}