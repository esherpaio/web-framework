function postShipmentMethods(data, silent = false) {
    const url = `/api/v1/shipment-methods`;
    return callApi('POST', url, data, 'application/json', silent);
}

function patchShipmentMethodsId(shipmentMethodId, data, silent = false) {
    const url = `/api/v1/shipment-methods/${shipmentMethodId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}

function deleteShipmentMethodsId(shipmentMethodId, silent = false) {
    const url = `/api/v1/shipment-methods/${shipmentMethodId}`;
    return callApi('DELETE', url, null, null, silent);
}