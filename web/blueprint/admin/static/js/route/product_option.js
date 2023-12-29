async function createOption(productId) {
    event.preventDefault();
    updateButton(`create-option`, 1);
    await postProductsIdOptions(productId, {
        name: document.getElementById(`option-name`).value
    });
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function updateOption(optionId, productId) {
    event.preventDefault();
    updateButton(`update-option-${optionId}`, 1);
    await patchProductsIdOptionsId(productId, optionId, {
        order: parseInt(document.getElementById(`option-order-${optionId}`).value),
    });
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function deleteOption(optionId, productId) {
    event.preventDefault();
    updateButton(`delete-option-${optionId}`, 1);
    await deleteProductsIdOptionsId(productId, optionId);
    await patchSetting({ cached_at: null });
    window.location.reload();
}