const callApi=async(method,url,data=null,contentType=null,silent=false)=>{if(method==="GET"&&data){let url_params="?";for(const[key,value]of Object.entries(data)){url_params+=`${key}=${value}`;}
url=`${url}${url_params}`;data=null;}
if(data&&contentType==="application/json"){data=JSON.stringify(data);}
const controller=new AbortController();const timeoutId=setTimeout(()=>controller.abort(),25000);let options={body:data,headers:{"Content-Type":contentType},method:method,signal:controller.signal,}
if(contentType===false){delete options.headers;}
let resp;return await fetch(url,options).then(data=>{return data.json();}).then(data=>{clearTimeout(timeoutId);resp=data;if(200<=resp.code&&resp.code<=299){return resp;}else{return Promise.reject();}}).catch(()=>{let message,error;if(resp&&resp.message){message=resp.message;error=resp.message;}else{message="Something went wrong on our end.";error="No response from API.";}
resetButtons();if(!silent){showMessage(message);throw new Error(error);}});}
async function initButtons(){const buttons=document.getElementsByClassName("btn-load");for(const button of buttons){button.dataset.loading="0";let spinner=document.createElement("span");spinner.classList.add('d-none','spinner-grow','spinner-grow-sm','ms-2');spinner.setAttribute("role","status");button.appendChild(spinner);}}
function resetButtons(){const buttons=document.getElementsByClassName("btn-load");for(const button of buttons){if(button.id){updateButton(button.id,0,true);}}}
function updateButton(buttonId,value,override){let button=document.getElementById(buttonId);if(!button.classList.contains('btn-load'))return;let spinner=button.getElementsByClassName('spinner-grow')[0];const oldCount=parseInt(button.dataset.loading);const newCount=override?value:oldCount+value;button.dataset.loading=String(newCount);if(newCount>0){button.setAttribute("disabled","");if(spinner.classList.contains('d-none')){spinner.classList.remove('d-none');}}else{button.removeAttribute("disabled");if(!spinner.classList.contains('d-none')){spinner.classList.add('d-none');}}}
window.addEventListener("load",()=>initButtons());
function postBillings(data,silent=false){const url=`/api/v1/billings`;return callApi('POST',url,data,'application/json',silent);}
function patchBillingsId(billingsId,data,silent=false){const url=`/api/v1/billings/${billingsId}`;return callApi('PATCH',url,data,'application/json',silent);}
function postCarts(silent=false){const url=`/api/v1/carts`;return callApi('POST',url,null,null,silent);}
function getCarts(silent=false){const url=`/api/v1/carts`;return callApi('GET',url,null,null,silent);}
function patchCartsId(cartId,data,silent=false){const url=`/api/v1/carts/${cartId}`;return callApi('PATCH',url,data,'application/json',silent);}
function deleteCartsId(cartId,silent=false){const url=`/api/v1/carts/${cartId}`;return callApi('DELETE',url,null,null,silent);}
function postCartsIdItems(cartId,data,silent=false){const url=`/api/v1/carts/${cartId}/items`;return callApi('POST',url,data,'application/json',silent);}
function patchCartIdItemsId(cartId,cartItemId,data,silent=false){const url=`/api/v1/carts/${cartId}/items/${cartItemId}`;return callApi('PATCH',url,data,'application/json',silent);}
function deleteCartIdItemsId(cartId,cartItemId,silent=false){const url=`/api/v1/carts/${cartId}/items/${cartItemId}`;return callApi('DELETE',url,null,null,silent);}
function postCategories(data,silent=false){const url=`/api/v1/categories`;return callApi('POST',url,data,'application/json',silent);}
function patchCategories(categoryId,data,silent=false){const url=`/api/v1/categories/${categoryId}`;return callApi('PATCH',url,data,'application/json',silent);}
function deleteCategoriesId(categoryId,silent=false){const url=`/api/v1/categories/${categoryId}`;return callApi('DELETE',url,null,null,silent);}
function postCategoriesIdItems(categoryId,data,silent=false){const url=`/api/v1/categories/${categoryId}/items`;return callApi('POST',url,data,'application/json',silent);}
function patchCategoriesIdItemsId(categoryId,itemId,data,silent=false){const url=`/api/v1/categories/${categoryId}/items/${itemId}`;return callApi('PATCH',url,data,'application/json',silent);}
function deleteCategoriesIdItemsId(categoryId,itemId,silent=false){const url=`/api/v1/categories/${categoryId}/items/${itemId}`;return callApi('DELETE',url,null,null,silent);}
function postCountries(data,silent=false){const url=`/api/v1/countries`;return callApi('POST',url,data,'application/json',silent);}
function getCountries(silent=false){const url=`/api/v1/countries`;return callApi('GET',url,null,null,silent);}
function getCountriesId(countryId,silent=false){const url=`/api/v1/countries/${countryId}`;return callApi('GET',url,null,null,silent);}
function deleteCountriesId(countryId,silent=false){const url=`/api/v1/countries/${countryId}`;return callApi('DELETE',url,null,null,silent);}
function postCoupons(data,silent=false){const url=`/api/v1/coupons`;return callApi('POST',url,data,'application/json',silent);}
function deleteCouponsId(couponId,silent=false){const url=`/api/v1/coupons/${couponId}`;return callApi('DELETE',url,null,null,silent);}
function postCurrencies(data,silent=false){const url=`/api/v1/currencies`;return callApi('POST',url,data,'application/json',silent);}
function getCurrencies(silent=false){const url=`/api/v1/currencies`;return callApi('GET',url,null,null,silent);}
function getCurrenciesId(currencyId,silent=false){const url=`/api/v1/currencies/${currencyId}`;return callApi('GET',url,null,null,silent);}
function deleteCurrenciesId(currencyId,silent=false){const url=`/api/v1/currencies/${currencyId}`;return callApi('DELETE',url,null,null,silent);}
function postEmails(data,silent=false){const url=`/api/v1/emails`;return callApi('POST',url,data,'application/json',silent);}
function postLanguages(data,silent=false){const url=`/api/v1/languages`;return callApi('POST',url,data,'application/json',silent);}
function getLanguages(silent=false){const url=`/api/v1/languages`;return callApi('GET',url,null,null,silent);}
function getLanguagesId(languageId,silent=false){const url=`/api/v1/languages/${languageId}`;return callApi('GET',url,null,null,silent);}
function deleteLanguagesId(languageId,silent=false){const url=`/api/v1/languages/${languageId}`;return callApi('DELETE',url,null,null,silent);}
function postOrders(data,silent=false){const url=`/api/v1/orders`;return callApi('POST',url,data,'application/json',silent);}
function deleteOrdersId(orderId,silent=false){const url=`/api/v1/orders/${orderId}`;return callApi('DELETE',url,null,null,silent);}
function postOrdersIdPayments(orderId,silent=false){const url=`/api/v1/orders/${orderId}/payments`;return callApi('POST',url,null,null,silent);}
function postOrdersIdRefunds(orderId,data,silent=false){const url=`/api/v1/orders/${orderId}/refunds`;return callApi('POST',url,data,'application/json',silent);}
function postProducts(data,silent=false){const url=`/api/v1/products`;return callApi('POST',url,data,'application/json',silent);}
function patchProductsId(productId,data,silent=false){const url=`/api/v1/products/${productId}`;return callApi('PATCH',url,data,'application/json',silent);}
function deleteProductsId(productId,silent=false){const url=`/api/v1/products/${productId}`;return callApi('DELETE',url,null,null,silent);}
function postProductsIdLinks(productId,data,silent=false){const url=`/api/v1/products/${productId}/links`;return callApi('POST',url,data,'application/json',silent);}
function deleteProductsIdLinksId(productId,linkId,silent=false){const url=`/api/v1/products/${productId}/links/${linkId}`;return callApi('DELETE',url,null,null,silent);}
function postProductsIdMedia(productId,data,silent=false){const url=`/api/v1/products/${productId}/media`;return callApi('POST',url,data,false,silent);}
function patchProductsIdMediaId(productId,mediaId,data,silent=false){const url=`/api/v1/products/${productId}/media/${mediaId}`;return callApi('PATCH',url,data,'application/json',silent);}
function deleteProductsIdMediaId(productId,mediaId,silent=false){const url=`/api/v1/products/${productId}/media/${mediaId}`;return callApi('DELETE',url,null,null,silent);}
function postProductsIdOptions(productId,data,silent=false){const url=`/api/v1/products/${productId}/options`;return callApi('POST',url,data,'application/json',silent);}
function patchProductsIdOptionsId(productId,optionId,data,silent=false){const url=`/api/v1/products/${productId}/options/${optionId}`;return callApi('PATCH',url,data,'application/json',silent);}
function deleteProductsIdOptionsId(productId,optionId,silent=false){const url=`/api/v1/products/${productId}/options/${optionId}`;return callApi('DELETE',url,null,null,silent);}
function postProductsIdSkus(productId,data,silent=false){const url=`/api/v1/products/${productId}/skus`;return callApi('POST',url,data,'application/json',silent);}
function postProductsIdValues(productId,data,silent=false){const url=`/api/v1/products/${productId}/values`;return callApi('POST',url,data,'application/json',silent);}
function patchProductsIdValuesId(productId,valueId,data,silent=false){const url=`/api/v1/products/${productId}/values/${valueId}`;return callApi('PATCH',url,data,'application/json',silent);}
function deleteProductsIdValuesId(productId,valueId,silent=false){const url=`/api/v1/products/${productId}/values/${valueId}`;return callApi('DELETE',url,null,null,silent);}
function postRegions(data,silent=false){const url=`/api/v1/regions`;return callApi('POST',url,data,'application/json',silent);}
function getRegions(silent=false){const url=`/api/v1/regions`;return callApi('GET',url,null,null,silent);}
function getRegionsId(regionId,silent=false){const url=`/api/v1/regions/${regionId}`;return callApi('GET',url,null,null,silent);}
function deleteRegionsId(regionId,silent=false){const url=`/api/v1/regions/${regionId}`;return callApi('DELETE',url,null,null,silent);}
function postSessions(data,silent=false){const url=`/api/v1/sessions`;return callApi('POST',url,data,'application/json',silent);}
function deleteSessions(silent=false){const url=`/api/v1/sessions`;return callApi('DELETE',url,null,'application/json',silent);}
function getSetting(silent=false){const url=`/api/v1/setting`;return callApi('GET',url,null,null,silent);}
function patchSetting(data,silent=false){const url=`/api/v1/setting`;return callApi('PATCH',url,data,'application/json',silent);}
function postOrdersIdShipments(orderId,data,silent=false){const url=`/api/v1/orders/${orderId}/shipments`;return callApi('POST',url,data,'application/json',silent);}
function postShipmentClasses(data,silent=false){const url=`/api/v1/shipment-classes`;return callApi('POST',url,data,'application/json',silent);}
function patchShipmentClassesId(shipmentClassId,data,silent=false){const url=`/api/v1/shipment-classes/${shipmentClassId}`;return callApi('PATCH',url,data,'application/json',silent);}
function deleteShipmentClassesId(shipmentClassId,silent=false){const url=`/api/v1/shipment-classes/${shipmentClassId}`;return callApi('DELETE',url,null,null,silent);}
function postShipmentMethods(data,silent=false){const url=`/api/v1/shipment-methods`;return callApi('POST',url,data,'application/json',silent);}
function patchShipmentMethodsId(shipmentMethodId,data,silent=false){const url=`/api/v1/shipment-methods/${shipmentMethodId}`;return callApi('PATCH',url,data,'application/json',silent);}
function deleteShipmentMethodsId(shipmentMethodId,silent=false){const url=`/api/v1/shipment-methods/${shipmentMethodId}`;return callApi('DELETE',url,null,null,silent);}
function postShipmentZones(data,silent=false){const url=`/api/v1/shipment-zones`;return callApi('POST',url,data,'application/json',silent);}
function patchShipmentZonesId(shipmentZoneId,data,silent=false){const url=`/api/v1/shipment-zones/${shipmentZoneId}`;return callApi('PATCH',url,data,'application/json',silent);}
function deleteShipmentZonesId(shipmentZoneId,silent=false){const url=`/api/v1/shipment-zones/${shipmentZoneId}`;return callApi('DELETE',url,null,null,silent);}
function postShippings(data,silent=false){const url=`/api/v1/shippings`;return callApi('POST',url,data,'application/json',silent);}
function getShippings(shippingId,silent=false){const url=`/api/v1/shippings/${shippingId}`;return callApi('GET',url,null,null,silent);}
function patchShippingsId(shippingsId,data,silent=false){const url=`/api/v1/shippings/${shippingsId}`;return callApi('PATCH',url,data,'application/json',silent);}
function postSkus(data,silent=false){const url=`/api/v1/skus`;return callApi('POST',url,data,'application/json',silent);}
function patchSkusId(skuId,data,silent=false){const url=`/api/v1/skus/${skuId}`;return callApi('PATCH',url,data,'application/json',silent);}
function deleteSkusId(skuId,silent=false){const url=`/api/v1/skus/${skuId}`;return callApi('DELETE',url,null,null,silent);}
function postUsers(data,silent=false){const url=`/api/v1/users`;return callApi('POST',url,data,'application/json',silent);}
function getUsers(data,silent=false){const url=`/api/v1/users`;return callApi('GET',url,data,null,silent);}
function getUsersId(userId,silent=false){const url=`/api/v1/users/${userId}`;return callApi('GET',url,null,null,silent);}
function patchUsersId(userId,data,silent=false){const url=`/api/v1/users/${userId}`;return callApi('PATCH',url,data,'application/json',silent);}
function postUsersIdActivation(userId,silent=false){const url=`/api/v1/users/${userId}/activation`;return callApi('POST',url,{},'application/json',silent);}
function patchUsersIdActivation(userId,data,silent=false){const url=`/api/v1/users/${userId}/activation`;return callApi('PATCH',url,data,'application/json',silent);}
function postUsersIdPassword(userId,silent=false){const url=`/api/v1/users/${userId}/password`;return callApi('POST',url,{},'application/json',silent);}
function patchUsersIdPassword(userId,data,silent=false){const url=`/api/v1/users/${userId}/password`;return callApi('PATCH',url,data,'application/json',silent);}
function getVerifications(data,silent=false){const url=`/api/v1/verifications`;return callApi('GET',url,data,null,silent);}
function showMessage(message){const elements=document.getElementsByClassName('modal');for(const element of elements){const modal=bootstrap.Modal.getInstance(element);if(modal)modal.hide();}
let modalBody=document.querySelector("#modal-message .modal-body p");modalBody.innerHTML=message;let modal=new bootstrap.Modal(document.getElementById('modal-message'));modal.show();}
function getParameter(key){let url=new URL(window.location.href);return url.searchParams.get(key);}
function removeParameter(key){let url=new URL(window.location.href);url.searchParams.delete(key);window.history.replaceState(null,null,url);}
function setParameter(key,value){let url=new URL(window.location.href);url.searchParams.set(key,value);window.history.replaceState(null,null,url);}
async function createCategoryItem(categoryId){event.preventDefault();updateButton(`create-category-item`,1);await postCategoriesIdItems(categoryId,{sku_id:parseInt(document.getElementById(`category-item-sku-id`).value),order:parseInt(document.getElementById('category-item-order').value),});await patchSetting({cached_at:null});window.location.reload();}
async function updateCategoryItem(categoryId,itemId){event.preventDefault();updateButton(`update-category-item-${itemId}`,1);await patchCategoriesIdItemsId(categoryId,itemId,{order:parseInt(document.getElementById(`category-item-order-${itemId}`).value)});await patchSetting({cached_at:null});window.location.reload();}
async function deleteCategoryItem(categoryId,itemId){event.preventDefault();updateButton(`delete-category-item-${itemId}`,1);await deleteCategoriesIdItemsId(categoryId,itemId);await patchSetting({cached_at:null});window.location.reload();}
async function createCategory(){event.preventDefault();updateButton('create-category',1);await postCategories({name:document.getElementById('category-name').value,order:parseInt(document.getElementById('category-order').value)});await patchSetting({cached_at:null});window.location.reload();}
async function updateCategory(categoryId){event.preventDefault();updateButton(`update-category-${categoryId}`,1);await patchCategories(categoryId,{child_id:parseInt(document.getElementById(`category-child-id-${categoryId}`).value),order:parseInt(document.getElementById(`category-order-${categoryId}`).value),in_header:document.getElementById(`category-in-header-${categoryId}`).checked,});await patchSetting({cached_at:null});window.location.reload();}
async function removeCategory(categoryId){event.preventDefault();updateButton(`delete-category-${categoryId}`,1);await deleteCategoriesId(categoryId);await patchSetting({cached_at:null});window.location.reload();}
async function createCoupon(){event.preventDefault();updateButton('create-coupon',1);await postCoupons({code:document.getElementById('coupon-code').value,percentage:parseInt(document.getElementById('coupon-percentage').value),amount:parseFloat(document.getElementById('coupon-amount').value)});window.location.reload();}
async function deleteCoupon(id){event.preventDefault();updateButton(`delete-coupon-${id}`,1);await deleteCouponsId(id);window.location.reload();}
async function cancelOrder(orderId){event.preventDefault();updateButton('cancel-order',1);await deleteOrdersId(orderId);window.location.reload();}
async function refundOrder(orderId){event.preventDefault();updateButton('create-refund',1);await postOrdersIdRefunds(orderId,{total_price:parseFloat(document.getElementById('refund-total-price').value),});window.location.reload();}
async function createShipment(orderId){event.preventDefault();updateButton('create-shipment',1);await postOrdersIdShipments(orderId,{url:document.getElementById('shipment-url').value,});window.location.reload();}
async function createLink(productId){event.preventDefault();updateButton(`create-link`,1);await postProductsIdLinks(productId,{type_id:parseInt(document.getElementById(`link-type-id`).value),sku_id:parseInt(document.getElementById(`link-sku-id`).value),});await patchSetting({cached_at:null});window.location.reload();}
async function deleteLink(id,productId){event.preventDefault();updateButton(`delete-link-${id}`,1);await deleteProductsIdLinksId(productId,id);await patchSetting({cached_at:null});window.location.reload();}
async function createMedia(productId){event.preventDefault();updateButton(`create-media`,1);let form=new FormData();const files=document.getElementById('media-files').files;for(let i=0;i<files.length;i++){form.append('file',files[i]);}
await postProductsIdMedia(productId,form);await patchSetting({cached_at:null});window.location.reload();}
async function updateMedia(id,productId){event.preventDefault();updateButton(`update-media-${id}`,1);await patchProductsIdMediaId(productId,id,{order:parseInt(document.getElementById(`media-order-${id}`).value),description:document.getElementById(`media-description-${id}`).value,});await patchSetting({cached_at:null});window.location.reload();}
async function deleteMedia(id,productId){event.preventDefault();updateButton(`delete-media-${id}`,1);await deleteProductsIdMediaId(productId,id);await patchSetting({cached_at:null});window.location.reload();}
async function createOption(productId){event.preventDefault();updateButton(`create-option`,1);await postProductsIdOptions(productId,{name:document.getElementById(`option-name`).value});await patchSetting({cached_at:null});window.location.reload();}
async function updateOption(optionId,productId){event.preventDefault();updateButton(`update-option-${optionId}`,1);await patchProductsIdOptionsId(productId,optionId,{order:parseInt(document.getElementById(`option-order-${optionId}`).value),});await patchSetting({cached_at:null});window.location.reload();}
async function deleteOption(optionId,productId){event.preventDefault();updateButton(`delete-option-${optionId}`,1);await deleteProductsIdOptionsId(productId,optionId);await patchSetting({cached_at:null});window.location.reload();}
async function createSkus(productId){event.preventDefault();updateButton(`create-skus`,1);await postProductsIdSkus(productId);await patchSetting({cached_at:null});window.location.reload();}
async function updateSku(id){event.preventDefault();updateButton(`update-sku-${id}`,1);await patchSkusId(id,{is_visible:document.getElementById(`sku-is-visible-${id}`).checked});await patchSetting({cached_at:null});window.location.reload();}
async function deleteSku(id){event.preventDefault();updateButton(`delete-sku-${id}`,1);await deleteSkusId(id);await patchSetting({cached_at:null});window.location.reload();}
async function createValue(optionId,productId){event.preventDefault();updateButton(`create-value`,1);await postProductsIdValues(productId,{name:document.getElementById('value-name').value,option_id:optionId,unit_price:parseFloat(document.getElementById('value-unit-price').value),});await patchSetting({cached_at:null});window.location.reload();}
async function updateValue(valueId,productId){event.preventDefault();updateButton(`update-value-${valueId}`,1);await patchProductsIdValuesId(productId,valueId,{media_id:parseInt(document.getElementById(`value-media-id-${valueId}`).value),order:parseInt(document.getElementById(`value-order-${valueId}`).value),unit_price:parseFloat(document.getElementById(`value-unit-price-${valueId}`).value),});await patchSetting({cached_at:null});window.location.reload();}
async function deleteValue(valueId,productId){event.preventDefault();updateButton(`delete-value-${valueId}`,1);await deleteProductsIdValuesId(productId,valueId);await patchSetting({cached_at:null});window.location.reload();}
async function createProduct(){event.preventDefault();updateButton(`create-product`,1);await postProducts({name:document.getElementById('product-name').value});await patchSetting({cached_at:null});window.location.reload();}
async function updateProduct(id){event.preventDefault();updateButton(`update-product`,1);await patchProductsId(id,{attributes:{html:htmlEditor.root.innerHTML,},type_id:parseInt(document.getElementById(`product-type-id`).value),shipment_class_id:parseInt(document.getElementById(`product-shipment-class-id`).value),unit_price:parseFloat(document.getElementById(`product-unit-price`).value),summary:document.getElementById(`product-summary`).value,consent_required:document.getElementById("product-consent-required").checked,file_url:document.getElementById("product-file-url").value,});await patchSetting({cached_at:null});window.location.reload();}
async function deleteProduct(id){event.preventDefault();updateButton(`delete-product`,1);let resp=await deleteProductsId(id);await patchSetting({cached_at:null});window.location=resp.links.products;}
async function logoutUser(){event.preventDefault();let element=event.currentTarget;await deleteSessions();let redirect=element.dataset.redirect;if(redirect){window.location.href=redirect;}}
async function updateSetting(){event.preventDefault();updateButton(`update-setting`,1);await patchSetting({banner:document.getElementById('setting-banner').value,cached_at:null,});window.location.reload();}
async function createShipmentClass(){event.preventDefault();updateButton('create-shipment-class',1);await postShipmentClasses({order:parseInt(document.getElementById('shipment-class-order').value),name:document.getElementById('shipment-class-name').value,});window.location.reload();}
async function updateShipmentClass(id){event.preventDefault();updateButton(`update-shipment-class-${id}`,1);await patchShipmentClassesId(id,{order:parseInt(document.getElementById(`shipment-class-order-${id}`).value)});window.location.reload();}
async function deleteshipmentClass(id){event.preventDefault();updateButton(`delete-shipment-class-${id}`,1);await deleteShipmentClassesId(id);window.location.reload();}
async function createShipmentMethod(){event.preventDefault();updateButton('create-shipment-method',1);await postShipmentMethods({name:document.getElementById('shipment-method-name').value,class_id:parseInt(document.getElementById(`shipment-method-class-id`).value),zone_id:parseInt(document.getElementById(`shipment-method-zone-id`).value),unit_price:parseFloat(document.getElementById(`shipment-method-unit-price`).value),});window.location.reload();}
async function updateShipmentMethod(id){event.preventDefault();updateButton(`update-shipment-method-${id}`,1);await patchShipmentMethodsId(id,{unit_price:parseFloat(document.getElementById(`shipment-method-unit-price-${id}`).value),phone_required:document.getElementById(`shipment-method-phone-required-${id}`).checked,});window.location.reload();}
async function deleteshipmentMethod(id){event.preventDefault();updateButton(`delete-shipment-method-${id}`,1);await deleteShipmentMethodsId(id);window.location.reload();}
async function createShipmentZone(){event.preventDefault();updateButton('create-shipment-zone',1);await postShipmentZones({order:parseInt(document.getElementById('shipment-zone-order').value),country_id:parseInt(document.getElementById(`shipment-zone-country-id`).value),region_id:parseInt(document.getElementById(`shipment-zone-region-id`).value)});window.location.reload();}
async function updateShipmentZone(id){event.preventDefault();updateButton(`update-shipment-zone-${id}`,1);await patchShipmentZonesId(id,{order:parseInt(document.getElementById(`shipment-zone-order-${id}`).value)});window.location.reload();}
async function deleteshipmentZone(id){event.preventDefault();updateButton(`delete-shipment-zone-${id}`,1);await deleteShipmentZonesId(id);window.location.reload();}
