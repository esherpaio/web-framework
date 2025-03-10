function isDict(value) {
    return (
        typeof value === "object" &&
        value !== null &&
        !Array.isArray(value) &&
        !(value instanceof Date)
    );
}

function isNumber(value) {
    return typeof value === "number" && !isNaN(value);
}
