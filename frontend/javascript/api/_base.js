const callApi = async (
    method,
    url,
    data = null,
    contentType = null,
    silent = false
) => {
    if (method === "GET" && data) {
        let url_params = "?";
        for (const [key, value] of Object.entries(data)) {
            url_params += `${key}=${value}`;
        }
        url = `${url}${url_params}`;
        data = null;
    }

    if (data && contentType === "application/json") {
        data = JSON.stringify(data);
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 25000);
    let options = {
        body: data,
        headers: { "Content-Type": contentType },
        method: method,
        signal: controller.signal,
    }
    if (contentType === false) {
        delete options.headers;
    }

    let resp;
    return await fetch(url, options).then(data => {
        return data.json();
    }).then(data => {
        clearTimeout(timeoutId);
        resp = data;
        if (200 <= resp.code && resp.code <= 299) {
            return resp;
        } else {
            return Promise.reject();
        }
    }).catch(() => {
        if (!silent) {
            let error;
            if (resp && resp.message) {
                error = resp.message;
            } else {
                error = "No response from API.";
            }
            throw new Error(error);
        }
    });
}