async function createProduct() {
    event.preventDefault();
    updateButton(`create-product`, 1);
    await postProducts({
        name: document.getElementById('product-name').value
    });
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function updateProduct(id) {
    event.preventDefault();
    updateButton(`update-product`, 1);
    await patchProductsId(id, {
        attributes: {
            html: htmlEditor.root.innerHTML,
        },
        type_id: parseInt(document.getElementById(`product-type-id`).value),
        shipment_class_id: parseInt(document.getElementById(`product-shipment-class-id`).value),
        unit_price: parseFloat(document.getElementById(`product-unit-price`).value),
        summary: document.getElementById(`product-summary`).value,
        consent_required: document.getElementById("product-consent-required").checked,
        file_url: document.getElementById("product-file-url").value,
    });
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function deleteProduct(id) {
    event.preventDefault();
    updateButton(`delete-product`, 1);
    let resp = await deleteProductsId(id);
    await patchSetting({ cached_at: null });
    window.location = resp.links.products;
}