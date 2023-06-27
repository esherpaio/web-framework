function postOrdersIdPayments(orderId, silent = false) {
    const url = `/api/v1/orders/${orderId}/payments`;
    return callApi('POST', url, null, null, silent);
}