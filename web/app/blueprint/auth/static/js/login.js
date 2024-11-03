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

async function checkParams() {
    const params = new URLSearchParams(window.location.search);
    const matchParam = 'verification_key';
    const match = params.has(matchParam);
    if (match) {
        const verificationKey = getParameter(matchParam);
        removeParameter(matchParam);
        await verifyUser(verificationKey);
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