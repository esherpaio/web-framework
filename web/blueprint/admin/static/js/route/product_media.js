async function createMedia(productId) {
    event.preventDefault();
    updateButton(`create-media`, 1);
    let form = new FormData();
    const files = document.getElementById('media-files').files;
    for (let i = 0; i < files.length; i++) {
        form.append('file', files[i]);
    }
    await postProductsIdMedia(productId, form);
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function updateMedia(id, productId) {
    event.preventDefault();
    updateButton(`update-media-${id}`, 1);
    await patchProductsIdMediaId(productId, id, {
        order: parseInt(document.getElementById(`media-order-${id}`).value),
        description: document.getElementById(`media-description-${id}`).value,
    });
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function deleteMedia(id, productId) {
    event.preventDefault();
    updateButton(`delete-media-${id}`, 1);
    await deleteProductsIdMediaId(productId, id);
    await patchSetting({ cached_at: null });
    window.location.reload();
}