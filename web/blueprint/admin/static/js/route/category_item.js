async function createCategoryItem(categoryId) {
    event.preventDefault();
    updateButton(`create-category-item`, 1);
    await postCategoriesIdItems(categoryId, {
        sku_id: parseInt(document.getElementById(`category-item-sku-id`).value),
        order: parseInt(document.getElementById('category-item-order').value),
    });
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function updateCategoryItem(categoryId, itemId) {
    event.preventDefault();
    updateButton(`update-category-item-${itemId}`, 1);
    await patchCategoriesIdItemsId(categoryId, itemId, {
        order: parseInt(document.getElementById(`category-item-order-${itemId}`).value)
    });
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function deleteCategoryItem(categoryId, itemId) {
    event.preventDefault();
    updateButton(`delete-category-item-${itemId}`, 1);
    await deleteCategoriesIdItemsId(categoryId, itemId);
    await patchSetting({ cached_at: null });
    window.location.reload();
}