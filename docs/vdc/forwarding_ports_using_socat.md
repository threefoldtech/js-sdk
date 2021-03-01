# To forward certain ports using socat to a specific service
in your chat flow do the following

```
@chatflow_step(title="forwardingports")
    def forward_ports(self):
        super()._forward_ports({
            "<service-name>": {"src": <src-port>, "dest": <destination-port>, "protocol": "TCP"}})

```
where
service-name: is your service name that you want to expose
src-port: the port on host you want your service to be reachable through
dest-port: the port of your service which is accessible from the cluster