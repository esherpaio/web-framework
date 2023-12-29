async function createLink(productId) {
    event.preventDefault();
    updateButton(`create-link`, 1);
    await postProductsIdLinks(productId, {
        type_id: parseInt(document.getElementById(`link-type-id`).value),
        sku_id: parseInt(document.getElementById(`link-sku-id`).value),
    });
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function deleteLink(id, productId) {
    event.preventDefault();
    updateButton(`delete-link-${id}`, 1);
    await deleteProductsIdLinksId(productId, id);
    await patchSetting({ cached_at: null });
    window.location.reload();
}