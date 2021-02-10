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
                    { text: "CU ($/mo)", value: "cu" },
                    { text: "SU ($/mo)", value: "su" },
                    { text: "IPv4U", value: "ipv4u" },
                    { text: "Actions", value: "action" },
                ],
                // csPricesInfo: [
                //     // { id: "50", name: "samar", cu: 32, su: 43, ip4u: 9 },
                //     // { id: "57", name: "sara", cu: 87, su: 45, ip4u: 54 },
                //     // { id: "89", name: "ehab", cu: 23, su: 34, ip4u: 68 },
                //     // { id: "32", name: "thabet", cu: 12, su: 46, ip4u: 76 },
                // ],
                openEditModal: false,
                openDeleteModal: false,
                deleteNodeFarmAlert: undefined,
                priceToEdit: { cu: 0, su: 0, ip4u: 0 },
                price: {},
                priceToDelete: { id: 0 }
            }
        },

        mounted() {
            this.loadPrices()
        },
        computed: {
            ...vuex.mapGetters("farmmanagement", ["customPricesList"]),

            tableName() {
                return `${this.farmselected.name} custom prices`
            }
        },
        methods: {
            ...vuex.mapActions("farmmanagement", [
                "getCustomPrices"
            ]),
            openEditPriceModal(node) {
                console.log(node)
                this.openEditModal = true
                this.priceToEdit = node
            },
            loadPrices() {
                this.getCustomPrices({ farmId: this.farmselected.id }).then(response => {
                    if (response.status == 200) {
                        this.csPricesInfo = JSON.parse(response.data).data;
                        console.log(this.csPricesInfo);
                    } else {
                        console.log("error...")
                    }
                })
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