module.exports = new Promise(async (resolve, reject) => {
    const vuex = await import("/weblibs/vuex/vuex.esm.browser.js");
    const { moment } = await import("/weblibs/moment/moment.min.js");
    const { momentDurationFormat } = await import(
        "/weblibs/moment/moment-duration-format.js"
    );
    const ipaddr = await import("https://cdn.jsdelivr.net/npm/ip-address@5.8.9/dist/ip-address-globals.js")
    momentDurationFormat(moment);
    resolve({
        name: "nodestable",
        props: ['farmselected'],
        components: {
            nodeinfo: "url:/farmmanagement/components/nodeinfo/index.vue"
        },
        data() {
            return {
                storeName: "",
                showDialog: false,
                dilogTitle: "title",
                dialogBody: "",
                dialogActions: [],
                dialogImage: null,
                block: null,
                showBadge: true,
                menu: false,
                loadedNodes: false,
                itemsPerPage: 4,
                expanded: [],
                searchNodes: "",
                headers: [
                    { text: "ID", value: "id" },
                    { text: "Uptime", value: "uptime" },
                    { text: "Version", value: "version" },
                    { text: "Status", value: "status", align: "center" },
                    { text: "Network Health", value: "healthy", align: "center" },
                    { text: "Actions", value: "action", sortable: false }
                ],
                openDeleteModal: false,
                deleteNodeFarmAlert: undefined,
                nodeToDelete: { id: 0 }
            }
        },
        computed: {
            ...vuex.mapGetters("farmmanagement", [
                "farms",
                "nodes"
            ]),
            // Parse nodelist to table format here
            parsedNodesList: function () {
                const nodeList = this.nodes

                const parsedNodes = nodeList.map(node => {
                    let healthy = false

                    let npub6Healthy = false
                    let npub4Healthy = false
                    let npub6HealthError, npub4HealthError, publicConfig6Error
                    let npub6Value, npub4Value, publicConfig6Value
                    let npub6Configs = []

                    const Global = "Global unicast"
                    const allowedIfaces = ["zos", "npub6", "npub4"]

                    if (node.ifaces) {
                        const ifaces = node.ifaces.filter(iface => allowedIfaces.includes(iface.name))
                        if (ifaces.length === 3) {
                            ifaces.map(iface => {
                                iface.addrs.map(addr => {
                                    switch (iface.name) {
                                        case "npub6": {
                                            const ip6 = new window.Address6(addr)
                                            if (ip6.isValid()) {
                                                if (ip6.getType() === Global) {
                                                    npub6Value = ip6.correctForm()
                                                    npub6Healthy = true
                                                } else {
                                                    console.log(`node with ${node.node_id} has ndmz private ip6`)
                                                    const correctForm = ip6.correctForm()
                                                    npub6Configs.push(correctForm)
                                                }
                                            }
                                        }
                                        case "npub4": {
                                            const ip4 = new window.Address4(addr)
                                            if (ip4.isValid()) {
                                                npub4Value = ip4.correctForm()
                                                npub4Healthy = true
                                            }
                                        }
                                    }
                                })
                            })
                        }
                    }

                    if (npub6Healthy && npub4Healthy) {
                        healthy = true
                    }

                    if (!npub6Healthy) {
                        npub6HealthError = "public ipv6 is missing on the NDMZ interface, please check your router configuration."
                    }
                    if (!npub4Healthy) {
                        npub4HealthError = "ipv4 is missing on the NDMZ interface, please check your router configuration."
                    }

                    if (npub6Healthy && npub6Healthy && node.public_config) {
                        const ip4 = new window.Address4(node.public_config.ipv4)
                        const ip6 = new window.Address6(node.public_config.ipv6)
                        if (ip4.isValid() && ip6.isValid()) {
                            // if public iface has a public ipv6 then the node is healthy
                            if (ip6.getType() !== Global) {
                                publicConfig6Value = ip6.correctForm()
                                publicConfig6Error = "public ipv6 is missing, please check your router configuration."
                                return healthy = false
                            }
                        }
                    }

                    return {
                        uptime: moment.duration(node.uptime, 'seconds').format(),
                        version: node.os_version,
                        id: node.node_id,
                        hostname: node.hostname,
                        farmer: this.farmselected,
                        name: 'node ' + node.node_id,
                        totalResources: node.total_resources,
                        reservedResources: node.reserved_resources,
                        usedResources: node.used_resources,
                        workloads: node.workloads,
                        updated: new Date(node.updated * 1000),
                        status: this.getStatus(node),
                        location: node.location,
                        free_to_use: node.free_to_use,
                        healthy,
                        npub6HealthError,
                        npub4HealthError,
                        publicConfig6Error,
                        npub6Value,
                        npub6Configs,
                        npub4Value,
                        publicConfig6Value
                    }
                })
                return parsedNodes
            },
        },
        methods: {
            ...vuex.mapActions("farmmanagement", [
                "deleteNodeFarm",
                "getNodes"
            ]),
            getStatus(node) {
                const { updated } = node;
                const startTime = moment();
                const end = moment.unix(updated);
                const minutes = startTime.diff(end, "minutes");

                // if updated difference in minutes with now is less then 10 minutes, node is up
                if (minutes < 15) return { color: "green", status: "up" };
                else if (16 < minutes && minutes < 20)
                    return { color: "orange", status: "likely down" };
                else return { color: "red", status: "down" };
            },
            truncateString(str) {
                str = str.toString();
                if (str.length < 10) return str;
                return str.substr(0, 10) + "...";
            },
            openNodeDetails(node) {
                const index = this.expanded.indexOf(node);
                if (index > -1) this.expanded.splice(index, 1);
                else this.expanded.push(node);
            },
            openDeleteNodeModal(node) {
                this.openDeleteModal = true
                this.nodeToDelete = node
            },
            deleteNode() {
                console.log(`Going to delete node with id: ${this.nodeToDelete.id}`)
                this.deleteNodeFarm(this.nodeToDelete)
                    .then(response => {
                        if (response.status == 200) {
                            this.deleteNodeFarmAlert = {
                                message: "node of farm deleted",
                                type: "success",
                            }
                        } else {
                            this.deleteNodeFarmAlert = {
                                message: response.data['error'],
                                type: "error",
                            }
                        }
                        setTimeout(() => {
                            this.deleteNodeFarmAlert = undefined
                        }, 2000)
                        this.openDeleteModal = false
                        this.getNodes(this.nodeToDelete.farmer.id)
                    }).catch(err => {
                        var msg = "server error"
                        if (err.response) {
                            // The request was made and the server responded with a status code
                            // that falls out of the range of 2xx
                            msg = err.response.data['error'] ? err.response.data['error'] : "server error"
                        }
                        this.deleteNodeFarmAlert = {
                            message: msg,
                            type: "error",
                        }
                        this.openDeleteModal = false
                        setTimeout(() => {
                            this.deleteNodeFarmAlert = undefined
                        }, 2000)
                    })
            }
        }
    });
});
