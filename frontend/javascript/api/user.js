function postUsers(data, silent = false) {
    const url = `/api/v1/users`;
    return callApi('POST', url, data, 'application/json', silent);
}

function getUsers(data, silent = false) {
    const url = `/api/v1/users`;
    return callApi('GET', url, data, null, silent);
}

function patchUsersId(userId, data, silent = false) {
    const url = `/api/v1/users/${userId}`;
    return callApi('PATCH', url, data, 'application/json', silent);
}

function postUsersIdActivation(userId, silent = false) {
    const url = `/api/v1/users/${userId}/activation`;
    return callApi('POST', url, {}, 'application/json', silent);
}

function patchUsersIdActivation(userId, data, silent = false) {
    const url = `/api/v1/users/${userId}/activation`;
    return callApi('PATCH', url, data, 'application/json', silent);
}

function postUsersIdPassword(userId, silent = false) {
    const url = `/api/v1/users/${userId}/password`;
    return callApi('POST', url, {}, 'application/json', silent);
}

function patchUsersIdPassword(userId, data, silent = false) {
    const url = `/api/v1/users/${userId}/password`;
    return callApi('PATCH', url, data, 'application/json', silent);
}