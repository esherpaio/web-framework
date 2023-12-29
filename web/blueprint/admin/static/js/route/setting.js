async function updateSetting() {
    event.preventDefault();
    updateButton(`update-setting`, 1);
    await patchSetting({
        banner: document.getElementById('setting-banner').value,
        cached_at: null,
    });
    window.location.reload();
}