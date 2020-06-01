const ajax = webix.ajax().headers({ "Content-Type": "application/json" });

export class Service {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    joinUrl(url) {
        if (this.baseUrl) {
            return `${this.baseUrl}/${url}`;
        }
        return url;
    }

    call(method, url, args) {
        method = method.toLowerCase();
        url = this.joinUrl(url);

        if (args) {
            args = { args: args };
        } else {
            args = {};
        }

        if (method === "get") {
            return ajax.get(url, args);
        } else if (method == "post") {
            return ajax.post(url, args);
        }

        throw ValueError(`${method} is not supported`);
    }

    getCall(url, args) {
        return this.call("get", url, args);
    }

    postCall(url, args) {
        return this.call("post", url, args);
    }
}
