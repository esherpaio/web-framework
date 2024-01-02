async function logoutUser(redirect) {
    await deleteSessions();
    await updateCartCount();
    if (redirect) {
        window.location.href = redirect;
    }
}