function postCoupons(data, silent = false) {
    const url = `/api/v1/coupons`;
    return callApi('POST', url, data, 'application/json', silent);
}

function deleteCouponsId(couponId, silent = false) {
    const url = `/api/v1/coupons/${couponId}`;
    return callApi('DELETE', url, null, null, silent);
}