/* verification key */

async function checkParams() {
    const params = new URLSearchParams(window.location.search);
    const matchParam = 'verification_key';
    const match = params.has(matchParam);
    if (match) {
        const verificationKey = getParameter(matchParam);
        removeParameter(matchParam);
        if (window.location.href.indexOf("/login") > -1) {
            await verifyUser(verificationKey);
        }
    }
}

async function verifyUser(verificationKey) {
    let resp = await getVerifications({ key: verificationKey });
    if (resp && resp.data.length > 0) {
        let verification = resp.data[0];
        resp = await patchUsersIdActivation(verification.user_id, { verification_key: verificationKey });
        showMessage(resp.message);
    }
}

window.addEventListener("load", checkParams);

/* login */

async function loginUser() {
    event.preventDefault();
    const buttonId = 'button-login-user';
    updateButton(buttonId, 1);
    await postSessions({
        email: document.getElementById('login-email').value,
        password: document.getElementById('login-password').value,
        remember: true,
    });
    window.location.href = URL_USER_LOGIN;
}

async function loginUserGoogle(resp) {
    const buttonId = 'button-login-user';
    updateButton(buttonId, 1);
    if (resp && resp.credential) {
        await postSessionsGoogle({ token_id: resp.credential });
        window.location.href = URL_USER_LOGIN;
    }
    updateButton(buttonId, -1);
}

/* register */

async function registerUser() {
    event.preventDefault();
    const buttonId = 'button-register-user';
    updateButton(buttonId, 1);
    let resp = await postUsers({
        email: document.getElementById('register-email').value,
        password: document.getElementById('register-password').value,
        password_eval: document.getElementById('register-password-eval').value,
    }, true);
    let message = resp.message;
    if (resp.code == 409) {
        resp = await getUsers({ email: document.getElementById('register-email').value })
        let user = resp.data.length > 0 ? resp.data[0] : null;
        if (user !== null && !user.is_active) {
            resp = await postUsersIdActivation(user.id);
            message = resp.message;
        }
    }
    showMessage(message);
    updateButton(buttonId, -1);
}

/* password */

async function requestPassword() {
    event.preventDefault();
    const buttonId = 'button-request-password';
    updateButton(buttonId, 1);
    let resp = await getUsers({ email: document.getElementById('request-email').value });
    if (resp && resp.data.length > 0) {
        let user = resp.data[0];
        resp = await postUsersIdPassword(user.id);
        showMessage(resp.message);
    }
    updateButton(buttonId, -1);
}

async function recoverPassword() {
    event.preventDefault();
    const buttonId = 'button-recover-password';
    updateButton(buttonId, 1);
    let resp = await getVerifications({ key: verificationKey });
    if (resp && resp.data.length > 0) {
        let verification = resp.data[0];
        resp = await patchUsersIdPassword(verification.user_id, {
            password: document.getElementById('recover-password').value,
            password_eval: document.getElementById('recover-password-eval').value,
            verification_key: verificationKey,
        });
        showMessage(resp.message);
    }
    updateButton(buttonId, -1);
}