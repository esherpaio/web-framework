async function checkParams() {
    const params = new URLSearchParams(window.location.search);
    const matchParam = 'verification_key';
    const match = params.has(matchParam);
    if (match) {
        const verificationKey = getParameter(matchParam);
        removeParameter(matchParam);
        if ((window.location.href.indexOf("/login") > -1)) {
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

window.addEventListener("load", () => {
    checkParams();
});