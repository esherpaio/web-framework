async function createShipmentZone() {
    event.preventDefault();
    updateButton('create-shipment-zone', 1);
    await postShipmentZones({
        order: parseInt(document.getElementById('shipment-zone-order').value),
        country_id: parseInt(document.getElementById(`shipment-zone-country-id`).value),
        region_id: parseInt(document.getElementById(`shipment-zone-region-id`).value)
    });
    window.location.reload();
}

async function updateShipmentZone(id) {
    event.preventDefault();
    updateButton(`update-shipment-zone-${id}`, 1);
    await patchShipmentZonesId(id, {
        order: parseInt(document.getElementById(`shipment-zone-order-${id}`).value)
    });
    window.location.reload();
}

async function deleteshipmentZone(id) {
    event.preventDefault();
    updateButton(`delete-shipment-zone-${id}`, 1);
    await deleteShipmentZonesId(id);
    window.location.reload();
}