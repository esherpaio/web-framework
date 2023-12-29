async function createCoupon() {
    event.preventDefault();
    updateButton('create-coupon', 1);
    await postCoupons({
        code: document.getElementById('coupon-code').value,
        percentage: parseInt(document.getElementById('coupon-percentage').value),
        amount: parseFloat(document.getElementById('coupon-amount').value)
    });
    window.location.reload();
}

async function deleteCoupon(id) {
    event.preventDefault();
    updateButton(`delete-coupon-${id}`, 1);
    await deleteCouponsId(id);
    window.location.reload();
}