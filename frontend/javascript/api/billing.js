function postBillings(data, silent = false) {
    const url = `/api/v1/billings`;
    return callApi('POST', url, data, 'application/json', silent);
}

function patchBillingsId(billingsId, data, silent = false) {
    const url = `/api/v1/billings/${billingsId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}