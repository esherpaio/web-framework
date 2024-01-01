function displayNav() {
    const sidebar = document.getElementById("sidebar");
    if (window.innerWidth >= 1200) {
        sidebar.classList.add("show");
        sidebar.classList.add("bg-secondary", "bg-opacity-25");
        sidebar.classList.remove("bg-light");
        sidebar.style.position = "relative";
    } else {
        sidebar.classList.remove("show");
        sidebar.classList.remove("bg-secondary", "bg-opacity-25");
        sidebar.classList.add("bg-light");
        sidebar.style.position = "absolute";
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

window.addEventListener("load", displayNav, false);
window.addEventListener("resize", displayNav, true);