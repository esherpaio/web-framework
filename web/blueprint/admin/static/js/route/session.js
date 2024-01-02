async function logoutUser() {
    event.preventDefault();
    let element = event.currentTarget;
    await deleteSessions();
    let redirect = element.dataset.redirect;
    if (redirect) {
        window.location.href = redirect;
    }
}