async function logoutUser() {
    let resp = await deleteSessions();
    await updateCartCount();
    window.location.href = resp.links.home;
}