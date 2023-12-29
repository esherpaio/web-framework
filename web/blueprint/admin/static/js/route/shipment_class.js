async function createShipmentClass() {
    event.preventDefault();
    updateButton('create-shipment-class', 1);
    await postShipmentClasses({
        order: parseInt(document.getElementById('shipment-class-order').value),
        name: document.getElementById('shipment-class-name').value,
    });
    window.location.reload();
}

async function updateShipmentClass(id) {
    event.preventDefault();
    updateButton(`update-shipment-class-${id}`, 1);
    await patchShipmentClassesId(id, {
        order: parseInt(document.getElementById(`shipment-class-order-${id}`).value)
    });
    window.location.reload();
}

async function deleteshipmentClass(id) {
    event.preventDefault();
    updateButton(`delete-shipment-class-${id}`, 1);
    await deleteShipmentClassesId(id);
    window.location.reload();
}