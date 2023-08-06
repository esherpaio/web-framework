function postUsersIdActivation(userId, silent = false) {
    const url = `/api/v1/users/${userId}/activation`;
    return callApi('POST', url, {}, 'application/json', silent);
}

function patchUsersIdActivation(userId, data, silent = false) {
    const url = `/api/v1/users/${userId}/activation`;
    return callApi('PATCH', url, data, 'application/json', silent);
}