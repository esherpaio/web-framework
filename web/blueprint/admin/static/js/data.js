function getCreateData(rowId) {
    return getData(document.querySelectorAll(`[data-create="None"]`));
}

function getEditdata(rowId) {
    return getData(document.querySelectorAll(`[data-edit="${rowId}"]`));
}

function getData(elements) {
    let data = {};
    for (let element of elements) {
        switch(element.dataset.variant) {
            case "string":
                data[element.name] = element.value;
                break;
            case "integer":
            case "foreign_key":
                data[element.name] = parseInt(element.value);
                break;
            case "float":
                data[element.name] = parseFloat(element.value);
                break;
            case "boolean":
                data[element.name] = element.checked;
                break;
        }
    }
    return data;
}

function isFloat(n) {
    return n.indexOf('.') == -1 ? false : true;
}