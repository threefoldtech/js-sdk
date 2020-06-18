class ActorsCollection {
    constructor(actorName, client) {
        this.actorName = actorName
        let actorHandler = {
            get(target, name) {
                let returned_func = function (actorArgs = {}, fetchOpts = {}) {
                    this.actorCmd = name
                    return client.executeCommand(actorName, name, actorArgs, fetchOpts);
                }
                return returned_func
            }
        }
        return new Proxy(client, actorHandler)
    }
}
class GedisHTTPClient {
    constructor(baseURL) {
        this.baseURL = baseURL
        this.client = this
        this.actorsCollectionHandler = {
            get(target, name) {
                return new ActorsCollection(name, target)
            }
        }
    }

    get actors() {
        return new Proxy(this.client, this.actorsCollectionHandler);
    }

    executeCommand(actorName, actorCmd, actorArgs = {}, fetchOpts = {}) {
        const url = `${this.baseURL}/${actorName}/${actorCmd}`
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


const localGedisClient = new GedisHTTPClient(`${location.protocol}//${location.hostname}/gedis/http`)
const tfGridGedisClient = new GedisHTTPClient(`https://explorer.testnet.grid.tf/gedis/http`)

/*
localGedisClient.executeCommand("alerta", "list_alerts").then( (resp) => console.log(resp.json()))
localGedisClient.actors.alerta.list_alerts().then((resp) => console.log(resp.json()))
*/
