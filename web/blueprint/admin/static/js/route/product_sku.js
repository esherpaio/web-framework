async function createSkus(productId) {
    event.preventDefault();
    updateButton(`create-skus`, 1);
    await postProductsIdSkus(productId);
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function updateSku(id) {
    event.preventDefault();
    updateButton(`update-sku-${id}`, 1);
    await patchSkusId(id, {
        is_visible: document.getElementById(`sku-is-visible-${id}`).checked
    });
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function deleteSku(id) {
    event.preventDefault();
    updateButton(`delete-sku-${id}`, 1);
    await deleteSkusId(id);
    await patchSetting({ cached_at: null });
    window.location.reload();
}