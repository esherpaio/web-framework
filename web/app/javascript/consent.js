async function initConsent() {
    let cookie = getCookie("consent");
    let element = document.getElementById("modal-consent");
    if (!cookie && element) {
        const modalOptions = { backdrop: "static", keyboard: false };
        const modal = new bootstrap.Modal(`#modal-consent`, modalOptions);
        modal.show();
    }
}

function setConsent(value) {
    setCookie("consent", value, 365);
    let event = value === 'true' ? 'consent_granted' : 'consent_denied';
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: event });

    const modalElement = document.getElementById("modal-consent");
    const modal = bootstrap.Modal.getInstance(modalElement);
    if (modal) modal.hide();
}

window.addEventListener("load", initConsent);
