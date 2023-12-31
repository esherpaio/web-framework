function initNav() {
    const sidebar = document.getElementById("sidebar");
    sidebar.style.flexGrow = "0";
    sidebar.style.flexShrink = "0";
    displayNav();
}

function displayNav() {
    const topbar = document.getElementById("topbar");
    const sidebar = document.getElementById("sidebar");
    if (window.innerWidth >= 1200) {
        sidebar.classList.add("show");
        sidebar.style.position = "relative";
        topbar.style.display = "none";
    } else {
        sidebar.classList.remove("show");
        sidebar.style.position = "absolute";
        topbar.style.display = "flex";
    }
}

function toggleNav() {
    const sidebar = document.getElementById("sidebar");
    const offcanvas = new bootstrap.Offcanvas('#sidebar')
    if (!sidebar.classList.contains("show")) {
        offcanvas.show();
        sidebar.style.position = "absolute";
    } else {
        offcanvas.hide();
        sidebar.style.position = "relative";
    }
}

window.addEventListener("load", initNav, false);
window.addEventListener("resize", displayNav, true);