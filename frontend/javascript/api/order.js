function postOrders(data, silent = false) {
    const url = `/api/v1/orders`;
    return callApi('POST', url, data, 'application/json', silent);
}

function deleteOrdersId(orderId, silent = false) {
    const url = `/api/v1/orders/${orderId}`;
    return callApi('DELETE', url, null, null, silent);
}