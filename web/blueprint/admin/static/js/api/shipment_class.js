function postShipmentClasses(data, silent = false) {
    const url = `/api/v1/shipment-classes`;
    return callApi('POST', url, data, 'application/json', silent);
}

function patchShipmentClassesId(shipmentClassId, data, silent = false) {
    const url = `/api/v1/shipment-classes/${shipmentClassId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}

function deleteShipmentClassesId(shipmentClassId, silent = false) {
    const url = `/api/v1/shipment-classes/${shipmentClassId}`;
    return callApi('DELETE', url, null, null, silent);
}