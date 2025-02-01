async function initConsent() {
    if (!getCookie('consent')) {
        const modalOptions = {
            backdrop: 'static',
            keyboard: false
        };
        const modal = new bootstrap.Modal(`#modal-consent`, modalOptions);
        modal.show();
    }
}

function setConsent(value) {
    setCookie('consent', value, 365);
    const modalElement = document.getElementById('modal-consent');
    const modal = bootstrap.Modal.getInstance(modalElement);
    if (modal) modal.hide();
}

window.addEventListener("load", initConsent);