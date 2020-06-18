class PackageActorsCollection {
    constructor(packageAuthor, packageName, actorName, client) {
        this.actorName = actorName
        let actorHandler = {
            get(target, name) {
                let returned_func = function (actorArgs = {}, fetchOpts = {}) {
                    this.actorCmd = name
                    return client.executeCommand(packageAuthor, packageName, actorName, name, actorArgs, fetchOpts);
                }
                return returned_func
            }
        }
        return new Proxy(client, actorHandler)
    }
}

class PackageGedisHTTPClient {
    constructor(packageAuthor, packageName, baseURL) {
        this.baseURL = baseURL
        this.client = this
        this.actorsCollectionHandler = {
            get(target, name) {
                return new PackageActorsCollection(packageAuthor, packageName, name, target)
            }
        }
    }

    get actors() {
        return new Proxy(this.client, this.actorsCollectionHandler);
    }

    executeCommand(packageAuthor, packageName, actorName, actorCmd, actorArgs = {}, fetchOpts = {}) {
        const url = `${this.baseURL}/${packageAuthor}/${packageName}/actors/${actorName}/${actorCmd}`
        let mainOpts = {
            method: 'POST', // *GET, POST, PUT, DELETE, etc.
            mode: 'cors', // no-cors, *cors, same-origin
            // cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            // // credentials: 'same-origin', // include, *same-origin, omit
            headers: {
                'Content-Type': 'application/json'
                // 'Content-Type': 'application/x-www-form-urlencoded',
            },
            redirect: 'follow', // manual, *follow, error
            referrer: 'no-referrer', // no-referrer, *client
            body: JSON.stringify({
                args: actorArgs
            }) // body data type must match "Content-Type" header
        }
        let opts = Object.assign(mainOpts, fetchOpts)
        console.log(url, opts)
        return fetch(url, opts);

    }
}


class BaseGedisHTTPClient {
    constructor(baseURL) {
        return new Proxy({}, {
            get: function (outerTarget, packageAuthor) {
                return new Proxy({}, {
                    get: function (innerTarget, packageName) {
                        return new PackageGedisHTTPClient(packageAuthor, packageName, baseURL);
                    }
                })
            }
        })
    }
}

const packageGedisClient = new BaseGedisHTTPClient(`${location.protocol}//${location.host}`);
