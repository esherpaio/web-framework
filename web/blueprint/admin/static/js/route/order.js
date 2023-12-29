async function cancelOrder(orderId) {
    event.preventDefault();
    updateButton('cancel-order', 1);
    await deleteOrdersId(orderId);
    window.location.reload();
}

async function refundOrder(orderId) {
    event.preventDefault();
    updateButton('create-refund', 1);
    await postOrdersIdRefunds(orderId, {
        total_price: parseFloat(document.getElementById('refund-total-price').value),
    });
    window.location.reload();
}

async function createShipment(orderId) {
    event.preventDefault();
    updateButton('create-shipment', 1);
    await postOrdersIdShipments(orderId, {
        url: document.getElementById('shipment-url').value,
    });
    window.location.reload();
}