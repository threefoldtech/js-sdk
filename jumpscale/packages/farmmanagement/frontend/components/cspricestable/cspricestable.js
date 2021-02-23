module.exports = new Promise(async (resolve, reject) => {
    const vuex = await
        import("/weblibs/vuex/vuex.esm.browser.js");
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
                    { text: "3Bot Name", value: "threebot_name" },
                    { text: "CU ($/mo)", value: "custom_cloudunits_price.cu" },
                    { text: "SU ($/mo)", value: "custom_cloudunits_price.su" },
                    { text: "IPv4U", value: "custom_cloudunits_price.ipv4u" },
                    { text: "Actions", value: "action" },
                ],
                openEditModal: false,
                openDeleteModal: false,
                deleteNodeFarmAlert: undefined,
                priceToEdit: { custom_cloudunits_price: { cu: 0, su: 0, ipv4u: 0 } },
                // price: {},
                priceToDelete: { id: 0 },
            }
        },

        mounted() {
            this.loadPrices()
        },
        computed: {
            ...vuex.mapGetters("farmmanagement", ["customPricesList", "farm"]),

            tableName() {
                return `${this.farm.name} custom prices`
            }
        },
        methods: {
            ...vuex.mapActions("farmmanagement", [
                "setCustomPricesList",
                "createOrUpdateFarmThreebotCustomPrice",
            ]),
            openEditPriceModal(node) {
                console.log("chose item: ", node)
                this.openEditModal = true
                this.priceToEdit = node //  {...node}; // Object.assign(this.priceToEdit, node); custom_cloudunits_price
                console.log("price to edit; ", this.priceToEdit)
            },
            loadPrices() {
                this.setCustomPricesList(this.farm.id)
                this.csPricesInfo = this.customPricesList
            },
            editPrice(id) {
                const updatedData = { farmId: this.priceToEdit.farm_id, threebotName: this.priceToEdit.threebot_name, prices: this.priceToEdit.custom_cloudunits_price }
                this.createOrUpdateFarmThreebotCustomPrice(updatedData).catch( () => {
                    this.loadPrices() // load old prices if failed to update
                })
                console.log("edit:   ", x)
                this.openEditModal = false
            },
            deleteModal(id) {
                this.openDeleteModal = true
                this.priceToDelete = id
            },
            closeEditModal() { this.openEditModal = false; this.loadPrices() },
            deleteprice() {
                // TODO: to be implemented
            },

        }
    });
});
