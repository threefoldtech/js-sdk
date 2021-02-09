module.exports = new Promise(async(resolve, reject) => {
    const vuex = await
    import ("/weblibs/vuex/vuex.esm.browser.js");
    resolve({
        name: "cspricestable",
        props: ['farmselected'],
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
                    { text: "ID", value: "id", },
                    { text: "3Bot name", value: "name" },
                    { text: "CU ($/mo)", value: "cu" },
                    { text: "SU ($/mo)", value: "su" },
                    { text: "IP4U", value: "ip4u" },
                    { text: "Actions", value: "action" },
                ],
                csPricesInfo: [
                    { id: "50", name: "samar", cu: 32, su: 43, ip4u: 9 },
                    { id: "57", name: "sara", cu: 87, su: 45, ip4u: 54 },
                    { id: "89", name: "ehab", cu: 23, su: 34, ip4u: 68 },
                    { id: "32", name: "thabet", cu: 12, su: 46, ip4u: 76 },
                ],
                openEditModal: false,
                openDeleteModal: false,
                deleteNodeFarmAlert: undefined,
                priceToEdit: { cu: 0, su: 0, ip4u: 0 },
                price: {},
                priceToDelete: { id: 0 }
            }
        },
        computed: {
            tableName() {
                return `${this.farmselected.name} custom prices`
            }
        },
        methods: {
            openEditPriceModal(node) {
                console.log(node)
                this.openEditModal = true
                this.priceToEdit = node
            },

            getRows(rows) {
                const result = {};
                _.forEach(rows, (i, key) => {
                    if (i.children) {
                        _.forEach(i.children, (i1, key1) => {
                            result["c" + key1] = i1;
                        });
                    } else result[key] = i;
                });
                return result;
            },

            getSubHeader(headers) {
                let result = [];
                headers
                    .filter((i) => i.children)
                    .forEach((v) => {
                        result = result.concat(v.children);
                    });
                return result;
            },

            editPrice(id) {
                console.log(id)
            },
            deleteModal(id) {
                this.openDeleteModal = true
                this.priceToDelete = id
            },
        }
    });
});