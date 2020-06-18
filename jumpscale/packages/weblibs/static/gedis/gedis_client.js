const GEDIS_CLIENT = (function () {
    let client = {};
    let protocol = "ws:"
    if(location.protocol == "https:"){
        protocol = "wss:"
    }
    let server = protocol + "//" + location.hostname + "/gedis/websocket"
    client.socket = new WebSocket(server);
    client.connected = false
    let connect = () => {
        return new Promise(res => {
            if (!client.connected) {
                client.socket.onopen = () => {
                    client.connected = true
                    res(true)
                }
            } else {
                res(true)
            }
        })
    }
    let execute = (namespace, actor, command, args, headers) => {
        return connect().then((res) => {
            return new Promise((resolve, fail) => {
                let message = {
                    "command": `${actor}.${command}`,
                    "args": args,
                    "headers": headers,
                }
                client.socket.send(JSON.stringify(message))
                client.socket.onmessage = function (e) {
                    resolve(e.data)
                }
            })
        })
    }
    client.execute = async (info) => {
        return await execute(info['namespace'], info['actor'], info['command'],
            info['args'], info['headers'])
    };
    return client
})()

info = { "namespace": "default", "actor": "system", "command": "ping" }
GEDIS_CLIENT.execute(info).then(res => console.log(res));
