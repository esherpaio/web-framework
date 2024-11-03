async function logoutUser() {
    await deleteSessions();
    await updateCartCount();
    window.location.href = URL_USER_LOGOUT;
}