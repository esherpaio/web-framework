function postShipmentZones(data, silent = false) {
    const url = `/api/v1/shipment-zones`;
    return callApi('POST', url, data, 'application/json', silent);
}

function patchShipmentZonesId(shipmentZoneId, data, silent = false) {
    const url = `/api/v1/shipment-zones/${shipmentZoneId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}

function deleteShipmentZonesId(shipmentZoneId, silent = false) {
    const url = `/api/v1/shipment-zones/${shipmentZoneId}`;
    return callApi('DELETE', url, null, null, silent);
}