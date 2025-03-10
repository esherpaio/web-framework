async function initCartCount() {
    let itemsCount = getCookie("items_count");
    if (isNaN(itemsCount)) itemsCount = 0;
    setCartCount(itemsCount);
}

async function updateCartCount(cart = undefined) {
    let itemsCount = 0;
    if (!cart) {
        let resp = await getCarts(true);
        if (resp && resp.data.length > 0) cart = resp.data[0];
    }
    if (cart) itemsCount = cart.items_count;
    setCartCount(itemsCount);
}

function setCartCount(value) {
    if (!isNaN(value)) {
        setCookie("items_count", value, 365);
        let element = document.getElementById("navbar-cart-count");
        if (element) element.innerText = value;
    }
}

window.addEventListener("load", initCartCount);
