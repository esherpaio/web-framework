async function createShipmentMethod() {
    event.preventDefault();
    updateButton('create-shipment-method', 1);
    await postShipmentMethods({
        name: document.getElementById('shipment-method-name').value,
        class_id: parseInt(document.getElementById(`shipment-method-class-id`).value),
        zone_id: parseInt(document.getElementById(`shipment-method-zone-id`).value),
        unit_price: parseFloat(document.getElementById(`shipment-method-unit-price`).value),
    });
    window.location.reload();
}

async function updateShipmentMethod(id) {
    event.preventDefault();
    updateButton(`update-shipment-method-${id}`, 1);
    await patchShipmentMethodsId(id, {
        unit_price: parseFloat(document.getElementById(`shipment-method-unit-price-${id}`).value),
        phone_required: document.getElementById(`shipment-method-phone-required-${id}`).checked,
    });
    window.location.reload();
}

async function deleteshipmentMethod(id) {
    event.preventDefault();
    updateButton(`delete-shipment-method-${id}`, 1);
    await deleteShipmentMethodsId(id);
    window.location.reload();
}