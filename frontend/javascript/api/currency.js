function postcurrencies(data, silent = false) {
    const url = `/api/v1/countries`;
    return callApi('POST', url, data, 'application/json', silent);
}

function getcurrencies(silent = false) {
    const url = `/api/v1/countries`;
    return callApi('GET', url, null, null, silent);
}

function getcurrenciesId(countryId, silent = false) {
    const url = `/api/v1/countries/${countryId}`;
    return callApi('GET', url, null, null, silent);
}

function deletecurrenciesId(countryId, silent = false) {
    const url = `/api/v1/countries/${countryId}`;
    return callApi('DELETE', url, null, null, silent);
}