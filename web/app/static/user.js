async function logoutUser() {
    await deleteSessions();
    window.location.href = URL_USER_LOGOUT;
}
