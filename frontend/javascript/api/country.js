function postCountries(data, silent = false) {
    const url = `/api/v1/countries`;
    return callApi('POST', url, data, 'application/json', silent);
}

function getCountries(silent = false) {
    const url = `/api/v1/countries`;
    return callApi('GET', url, null, null, silent);
}

function getCountriesId(countryId, silent = false) {
    const url = `/api/v1/countries/${countryId}`;
    return callApi('GET', url, null, null, silent);
}

function deleteCountriesId(countryId, silent = false) {
    const url = `/api/v1/countries/${countryId}`;
    return callApi('DELETE', url, null, null, silent);
}