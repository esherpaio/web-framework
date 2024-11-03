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

async function checkParams() {
    const params = new URLSearchParams(window.location.search);
    const matchParam = 'verification_key';
    const match = params.has(matchParam);
    if (match) {
        const verificationKey = getParameter(matchParam);
        removeParameter(matchParam);
    }
}

window.addEventListener("load", checkParams);