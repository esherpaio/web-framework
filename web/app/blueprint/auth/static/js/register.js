async function registerUser() {
    event.preventDefault();
    const buttonId = 'button-register-user';
    updateButton(buttonId, 1);
    let resp = await postUsers({
        email: document.getElementById('register-email').value,
        password: document.getElementById('register-password').value,
        password_eval: document.getElementById('register-password-eval').value,
    });
    let user = resp.data;
    resp = await postUsersIdActivation(user.id);
    showMessage(resp.message);
    updateButton(buttonId, -1);
}