async function logoutUser() {
    event.preventDefault();
    await deleteSessions();
    await updateCartCount();
    let element = event.currentTarget;
    let redirect = element.dataset.redirect;
    if (redirect) {
        window.location.href = redirect;
    }
}