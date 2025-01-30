// cart item actions
async function loadCartItems(cart, currency) {
    const tableBody = document.querySelector("#cart-items tbody");
    tableBody.innerHTML = "";
    const cartItems = (await getCartsIdItems(cart.id)).data;
    for (const cartItem of cartItems) {
        const tr = document.createElement('tr');
        tableBody.appendChild(tr);

        const idTd = document.createElement('td');
        idTd.textContent = cartItem.id;
        tr.appendChild(idTd);

        const skuNameTd = document.createElement('td');
        skuNameTd.textContent = cartItem.sku_name;
        tr.appendChild(skuNameTd);

        const quantityTd = document.createElement('td');
        tr.appendChild(quantityTd);
        const quantityTdInput = document.createElement('input');
        quantityTdInput.id = `cart-item-quantity-${cartItem.id}`;
        quantityTdInput.classList.add("form-control", "form-control-sm", "reload-page");
        quantityTdInput.type = "number";
        quantityTdInput.value = cartItem.quantity;
        quantityTd.append(quantityTdInput);

        const unitPriceTd = document.createElement('td');
        unitPriceTd.textContent = `${cartItem.unit_price} ${currency.code}`;
        tr.appendChild(unitPriceTd);

        const selectionTd = document.createElement('td');
        selectionTd.classList.add('text-end');
        tr.appendChild(selectionTd);
        const selectionTdDiv = document.createElement('div');
        selectionTdDiv.classList.add("btn-group");
        selectionTd.append(selectionTdDiv);
        const selectionButtonUpdate = document.createElement('a');
        selectionButtonUpdate.id = `update-cart-item-${cartItem.id}`;
        selectionButtonUpdate.dataset.cartId = cartItem.cart_id;
        selectionButtonUpdate.dataset.cartItemId = cartItem.id;
        selectionButtonUpdate.classList.add("btn", "btn-load", "btn-sm", "btn-outline-primary");
        selectionButtonUpdate.addEventListener("click", (e) => updateCartItem(e));
        selectionButtonUpdate.textContent = "Update";
        selectionTdDiv.append(selectionButtonUpdate);
        const selectionButtonDelete = document.createElement('a');
        selectionButtonDelete.id = `delete-cart-item-${cartItem.id}`;
        selectionButtonDelete.dataset.cartId = cartItem.cart_id;
        selectionButtonDelete.dataset.cartItemId = cartItem.id;
        selectionButtonDelete.classList.add("btn", "btn-load", "btn-sm", "btn-outline-danger");
        selectionButtonDelete.addEventListener("click", (e) => deleteCartItem(e));
        selectionButtonDelete.textContent = "Delete";
        selectionTdDiv.append(selectionButtonDelete);
    }
}
async function addCartItem(event) {
    const cartId = parseInt(event.target.dataset.cartId);
    await updateButton(`add-cart-item`, 1);
    const skuEl = document.querySelector('input[name="sku-id"]:checked');
    const skuId = parseInt(skuEl.value);
    const cartData = { sku_id: parseInt(skuId), quantity: 1 };
    await postCartsIdItems(cartId, cartData);
    await reloadPage();
    await updateButton(`add-cart-item`, -1);
}
async function updateCartItem(event) {
    const cartId = parseInt(event.target.dataset.cartId);
    const cartItemId = parseInt(event.target.dataset.cartItemId);
    await updateButton(`update-cart-item-${cartItemId}`, 1);
    const cartItemQuantityEl = document.getElementById(`cart-item-quantity-${cartItemId}`);
    const cartItemQuantity = parseInt(cartItemQuantityEl.value);
    const cartData = { quantity: cartItemQuantity };
    await patchCartIdItemsId(cartId, cartItemId, cartData);
    await reloadPage();
    await updateButton(`update-cart-item-${cartItemId}`, -1);
}
async function deleteCartItem(event) {
    const cartId = parseInt(event.target.dataset.cartId);
    const cartItemId = parseInt(event.target.dataset.cartItemId);
    await updateButton(`delete-cart-item-${cartItemId}`, 1);
    await deleteCartIdItemsId(cartId, cartItemId);
    await reloadPage();
    await updateButton(`delete-cart-item-${cartItemId}`, -1);
}

// shipping actions
async function loadShipping(shipping, countries) {
    const countrySelect = document.getElementById('shipping-country-id');
    countrySelect.options.length = 0;
    for (const country of countries) {
        const countryOption = document.createElement('option');
        countryOption.value = country.id;
        countryOption.textContent = country.name;
        countrySelect.appendChild(countryOption);
    };

    const idNames = ["address", "city", "country-id", "email", "first-name", "last-name", "phone", "state", "zip-code"];
    for (const idName of idNames) {
        const key = idName.replace(/-/g, "_");
        const value = shipping[key];
        if (value !== undefined) {
            document.getElementById(`shipping-${idName}`).value = value;
        } else {
            document.getElementById(`shipping-${idName}`).value = "";
        }
    }
}
async function updateShipping(cart, silent = false) {
    const shippingData = emptyStrToNull({
        address: document.getElementById('shipping-address').value,
        city: document.getElementById('shipping-city').value,
        country_id: parseInt(document.getElementById('shipping-country-id').value),
        email: document.getElementById('shipping-email').value,
        first_name: document.getElementById('shipping-first-name').value,
        last_name: document.getElementById('shipping-last-name').value,
        phone: document.getElementById('shipping-phone').value,
        state: document.getElementById('shipping-state').value,
        zip_code: document.getElementById('shipping-zip-code').value,
    });
    let shipping;
    if (cart.shipping_id) {
        shipping = (await patchShippingsId(cart.shipping_id, shippingData, silent)).data;
    }
    if (!shipping) {
        shipping = (await postShippings(cartData, silent)).data;
    }
    const cartData = { shipping_id: shipping.id };
    await patchCartsId(cart.id, cartData, silent);
    return shipping;
}

// billing actions
async function loadBilling(billing, countries) {
    const countrySelect = document.getElementById('billing-country-id');
    countrySelect.options.length = 0;
    for (const country of countries) {
        const countryOption = document.createElement('option');
        countryOption.value = country.id;
        countryOption.textContent = country.name;
        countrySelect.appendChild(countryOption);
    };

    const idNames = ["address", "city", "country-id", "email", "first-name", "last-name", "phone", "state", "zip-code", "company", "vat"];
    for (const idName of idNames) {
        const key = idName.replace(/-/g, "_");
        const value = billing[key];
        if (value !== undefined) {
            document.getElementById(`billing-${idName}`).value = value;
        } else {
            document.getElementById(`billing-${idName}`).value = "";
        }
    }
}
async function updateBilling(cart, silent = false) {
    const billingData = emptyStrToNull({
        address: document.getElementById('billing-address').value,
        city: document.getElementById('billing-city').value,
        company: document.getElementById('billing-company').value,
        country_id: parseInt(document.getElementById('billing-country-id').value),
        email: document.getElementById('billing-email').value,
        first_name: document.getElementById('billing-first-name').value,
        last_name: document.getElementById('billing-last-name').value,
        phone: document.getElementById('billing-phone').value,
        state: document.getElementById('billing-state').value,
        vat: document.getElementById('billing-vat').value,
        zip_code: document.getElementById('billing-zip-code').value,
    });
    let billing;
    if (cart.billing_id) {
        billing = (await patchBillingsId(cart.billing_id, billingData, silent)).data;
    }
    if (!billing) {
        billing = (await postBillings(cartData, silent)).data;
    }
    const cartData = { billing_id: billing.id };
    await patchCartsId(cart.id, cartData, silent);
    return billing;
}
async function copyShippingToBilling() {
    const checkbox = document.getElementById("checkbox-use-shipping-for-billing");
    if (!checkbox.checked) return;
    const idNames = ["address", "city", "country-id", "email", "first-name", "last-name", "phone", "state", "zip-code"];
    for (const idName of idNames) {
        const shippingValue = document.getElementById(`shipping-${idName}`).value;
        document.getElementById(`billing-${idName}`).value = shippingValue;
    }
}

// shipment method actions
async function loadShipmentMethods(cart, currency) {
    const tableBody = document.querySelector("#shipment-methods tbody");
    tableBody.innerHTML = "";
    const shipmentMethods = (await getShipmentMethods({ "cart_id": cart.id })).data;
    for (const shipmentMethod of shipmentMethods) {
        const tr = document.createElement('tr');
        tableBody.appendChild(tr);

        const nameTd = document.createElement('td');
        nameTd.textContent = shipmentMethod.name;
        tr.appendChild(nameTd);

        const priceTd = document.createElement('td');
        priceTd.textContent = `${shipmentMethod.unit_price} ${currency.code}`;
        tr.appendChild(priceTd);

        const selectionTd = document.createElement('td');
        selectionTd.classList.add('text-end');
        tr.appendChild(selectionTd);
        const selectionTdDiv = document.createElement('div');
        selectionTdDiv.classList.add('form-check', 'd-flex', 'justify-content-end');
        selectionTd.appendChild(selectionTdDiv);
        const selectionInput = document.createElement('input');
        selectionInput.id = `shipment-method-${shipmentMethod.id}`;
        selectionInput.classList.add('form-check-input');
        selectionInput.type = 'radio';
        selectionInput.name = 'shipment-method-id';
        selectionInput.value = `${shipmentMethod.id}`;
        selectionInput.addEventListener("click", () => updateShipmentMethod(cart));
        if (shipmentMethod.id === cart.shipment_method_id) {
            selectionInput.checked = true;
        }
        selectionTdDiv.appendChild(selectionInput);
    }
}
async function updateShipmentMethod(cart) {
    const shipmentMethodEl = document.querySelector('input[name="shipment-method-id"]:checked');
    let shipmentMethodId;
    if (shipmentMethodEl) {
        shipmentMethodId = parseInt(shipmentMethodEl.value);
    } else {
        shipmentMethodId = null;
    }
    const cartData = { shipment_method_id: shipmentMethodId };
    await patchCartsId(cart.id, cartData);

    const shipmentMethod = (await getShipmentMethodsId(shipmentMethodId)).data;
    const billingPhoneEl = document.getElementById("billing-phone");
    billingPhoneEl.required = shipmentMethod.phone_required;
}

// order actions
async function loadAddOrderButton(cart) {
    const addOrderButton = document.getElementById("add-order");
    addOrderButton.dataset.cartId = cart.id;
    addOrderButton.addEventListener("click", (e) => addOrder(e));
}
async function addOrder(event) {
    const cartId = parseInt(event.target.dataset.cartId);
    const cart = (await getCartsId(cartId)).data;
    const orderData = { 'cart_id': cart.id, 'trigger_mail': false };
    const order = (await postOrders(orderData)).data;
    const mollieRedirect = `${location.protocol}//${location.host}`;
    const redirect = `${location.protocol}//${location.host}${URL_ADMIN_ORDERS}/${order.id}`;
    await postOrdersIdPayments(order.id, { "redirect": mollieRedirect });
    window.location.href = redirect;
}

// sku actions
async function loadSkus(cart, skus) {
    const tableBody = document.querySelector("#skus tbody");
    tableBody.innerHTML = "";
    for (const sku of skus) {
        const tr = document.createElement('tr');
        tableBody.appendChild(tr);

        const idTd = document.createElement('td');
        idTd.textContent = sku.id;
        tr.appendChild(idTd);

        const nameTd = document.createElement('td');
        nameTd.textContent = sku.name;
        tr.appendChild(nameTd);

        const selectionTd = document.createElement('td');
        selectionTd.classList.add('text-end');
        tr.appendChild(selectionTd);
        const selectionTdDiv = document.createElement('div');
        selectionTdDiv.classList.add('form-check', 'd-flex', 'justify-content-end');
        selectionTd.appendChild(selectionTdDiv);
        const selectionInput = document.createElement('input');
        selectionInput.id = `sku-${sku.id}`;
        selectionInput.classList.add('form-check-input');
        selectionInput.type = 'radio';
        selectionInput.name = 'sku-id';
        selectionInput.value = `${sku.id}`;
        selectionTdDiv.appendChild(selectionInput);
    }

    const addCartItemButton = document.getElementById("add-cart-item");
    addCartItemButton.dataset.cartId = cart.id;
    addCartItemButton.addEventListener("click", (e) => addCartItem(e));
}

// initialization
async function loadPage() {
    const cart = (await getCarts()).data[0];
    const currency = (await getCurrenciesId(cart.currency_id)).data;
    const countries = (await getCountries()).data;
    const user = (await getUsersId(cart.user_id)).data;
    const skus = (await getSkus()).data;

    let shipping_id = null;
    if (cart.shipping_id) {
        shipping_id = cart.shipping_id;
    } else if (user.shipping_id) {
        shipping_id = user.shipping_id;
    }
    if (shipping_id !== null) {
        const shipping = (await getShippingsId(shipping_id)).data;
        await loadShipping(shipping, countries);
    }

    let billing_id = null;
    if (cart.billing_id) {
        billing_id = cart.billing_id;
    } else if (user.billing_id) {
        billing_id = user.billing_id;
    }
    if (billing_id !== null) {
        const billing = (await getBillingsId(billing_id)).data;
        await loadBilling(billing, countries);
    }

    await loadCartItems(cart, currency);
    await loadShipmentMethods(cart, currency);
    await loadSkus(cart, skus);
    await loadAddOrderButton(cart);
    await initButtons();

    const debounceCopyShippingToBilling = debounce(copyShippingToBilling, 100);
    const debounceReloadPage = debounce(reloadPage, 100);
    document.addEventListener('change', (event) => {
        if (event.target.matches('.copy-billing')) {
            debounceCopyShippingToBilling();
        }
        if (event.target.matches('.reload-page')) {
            debounceReloadPage();
        }
    });
}
async function reloadPage() {
    let cart = (await getCarts()).data[0];
    const shipping = await updateShipping(cart, true);
    const billing = await updateBilling(cart, true);
    cart = (await getCarts()).data[0];
    const currency = (await getCurrenciesId(cart.currency_id)).data;
    const countries = (await getCountries()).data;
    await loadShipping(shipping, countries);
    await loadBilling(billing, countries);
    await loadCartItems(cart, currency);
    await loadShipmentMethods(cart, currency);
    await initButtons();
}
document.addEventListener("DOMContentLoaded", loadPage);