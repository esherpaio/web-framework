function postCurrencies(data, silent = false) {
    const url = `/api/v1/currencies`;
    return callApi('POST', url, data, 'application/json', silent);
}

function getCurrencies(silent = false) {
    const url = `/api/v1/currencies`;
    return callApi('GET', url, null, null, silent);
}

function getCurrenciesId(currencyId, silent = false) {
    const url = `/api/v1/currencies/${currencyId}`;
    return callApi('GET', url, null, null, silent);
}

function deleteCurrenciesId(currencyId, silent = false) {
    const url = `/api/v1/currencies/${currencyId}`;
    return callApi('DELETE', url, null, null, silent);
}