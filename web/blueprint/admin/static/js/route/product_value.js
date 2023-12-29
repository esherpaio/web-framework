async function createValue(optionId, productId) {
    event.preventDefault();
    updateButton(`create-value`, 1);
    await postProductsIdValues(productId, {
        name: document.getElementById('value-name').value,
        option_id: optionId,
        unit_price: parseFloat(document.getElementById('value-unit-price').value),
    });
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function updateValue(valueId, productId) {
    event.preventDefault();
    updateButton(`update-value-${valueId}`, 1);
    await patchProductsIdValuesId(productId, valueId, {
        media_id: parseInt(document.getElementById(`value-media-id-${valueId}`).value),
        order: parseInt(document.getElementById(`value-order-${valueId}`).value),
        unit_price: parseFloat(document.getElementById(`value-unit-price-${valueId}`).value),
    });
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function deleteValue(valueId, productId) {
    event.preventDefault();
    updateButton(`delete-value-${valueId}`, 1);
    await deleteProductsIdValuesId(productId, valueId);
    await patchSetting({ cached_at: null });
    window.location.reload();
}