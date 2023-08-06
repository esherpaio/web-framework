function postUsersIdPassword(userId, silent = false) {
    const url = `/api/v1/users/${userId}/password`;
    return callApi('POST', url, {}, 'application/json', silent);
}

function patchUsersIdPassword(userId, data, silent = false) {
    const url = `/api/v1/users/${userId}/password`;
    return callApi('PATCH', url, data, 'application/json', silent);
}