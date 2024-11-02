async function loginUser() {
    event.preventDefault();
    const buttonId = 'button-login-user';
    updateButton(buttonId, 1);
    await postSessions({
        email: document.getElementById('login-email').value,
        password: document.getElementById('login-password').value,
        remember: true,
    });
    await updateCartCount();
    window.location.href = URL_USER_SETTINGS;
}

async function loginUserGoogle(resp) {
    const buttonId = 'button-login-user';
    updateButton(buttonId, 1);
    if (resp && resp.credential) {
        await postSessionsGoogle({ token_id: resp.credential });
        window.location.href = URL_USER_SETTINGS;
    }
    updateButton(buttonId, -1);
}