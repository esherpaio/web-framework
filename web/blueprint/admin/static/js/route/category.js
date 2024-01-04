async function createCategory() {
    event.preventDefault();
    updateButton('create-category', 1);
    await postCategories({
        name: document.getElementById('category-name').value,
        order: parseInt(document.getElementById('category-order').value)
    });
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function updateCategory(categoryId) {
    event.preventDefault();
    updateButton(`update-category-${categoryId}`, 1);
    await patchCategories(categoryId, {
        child_id: parseInt(document.getElementById(`category-child-id-${categoryId}`).value),
        order: parseInt(document.getElementById(`category-order-${categoryId}`).value),
        in_header: document.getElementById(`category-in-header-${categoryId}`).checked,
    });
    await patchSetting({ cached_at: null });
    window.location.reload();
}

async function removeCategory(categoryId) {
    event.preventDefault();
    updateButton(`delete-category-${categoryId}`, 1);
    await deleteCategoriesId(categoryId);
    await patchSetting({ cached_at: null });
    window.location.reload();
}