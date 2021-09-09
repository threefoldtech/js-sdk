// require('./farmmanagement/weblibs/gmaps/vue-google-maps.js')
module.exports = new Promise(async (resolve, reject) => {
    const vuex = await
        import(
            "/weblibs/vuex/vuex.esm.browser.js"
        );
    resolve({
        name: "farmManagement",
        components: {
            nodestable: "url:/farmmanagement/components/nodestable/index.vue",
            cspricestable: "url:/farmmanagement/components/cspricestable/index.vue",
        },
        data() {
            return {
                refreshInterval: undefined,
                addFarmDialog: false,
                addNodeDialog: false,
                settingsDialog: false,
                showSetFarmPrice: false,
                farmDescriptionRules: [v => v.length <= 250 || "Max 250 characters"],
                searchFarms: "",
                'searchnodes': "",
                farmSelected: {},
                farmToEdit: {},
                editFarmAlert: undefined,
                showResult: false,
                itemsPerPage: 4,
                expanded: [],
                addCustomModelError: null,
                headers: [
                    { text: "Id", value: "id" },
                    {
                        text: "Farm name",
                        sortable: false,
                        value: "name"
                    },
                    { text: "CU ($/mo)", value: "cu" },
                    { text: "SU ($/mo)", value: "su" },
                    { text: "IPv4u ($/mo)", value: "ipv4u" },
                    { text: "Actions", value: "action", sortable: false }
                ],
                prices: [{ node: 3 }, { node: 8 }],
                newFarm: {
                    threebot_id: "",
                    location: {
                        latitude: 0,
                        longitude: 0
                    },
                    wallet_addresses: [],
                    // resource_prices: [
                    //     {
                    //         currency: "USD",
                    //         cru: 0,
                    //         mru: 0,
                    //         hru: 0,
                    //         sru: 0,
                    //         nru: 0
                    //     }
                    // ]
                },
                farm_price: {
                    cu: null,
                    su: null,
                    ipv4u: null
                },
                customPrice: {
                    threebotName: '',
                    cu: null,
                    su: null,
                    ipv4u: null,
                    threebotId: null
                },
                newFarmAlert: undefined,
                priceUpdate: undefined,
                searchAddressInput: "",
                openAddCustomModel: false,
                namerules: [v => !!v || "Name is required"],
                nameError: [],
                mailError: [],
                countries: getCountries(),
                loading: false,
                upgrade: false,
                showUpgradeConfirmation: false,
            }
        },
        computed: {
            ...vuex.mapGetters("farmmanagement", ["farms", "nodes", "farm", "user", "tfgridUrl", "customPricesList"]),
            parsedLocation() {
                return {
                    lat: this.newFarm.location.latitude,
                    lng: this.newFarm.location.longitude
                };
            },
        },
        async mounted() {
            await this.getTfgridUrl();
            await this.getUser();
            await this.getFarms();
            this.initialiseRefresh()
            this.newFarm.threebot_id = this.user.id;
        },
        methods: {
            ...vuex.mapActions("farmmanagement", [
                "getUser",
                "registerFarm",
                "getFarms",
                "getNodes",
                "getTfgridUrl",
                "setCustomPricesList",
                "setDefaultFarmPrices",
                "createOrUpdateFarmThreebotCustomPrice",
                "setFarm",
                "updateFarm",
            ]),
            upgradeToGrid3(farm) {
                this.upgrade = true;
                // change the grid 3 flag to be true
                farm.is_grid3_compliant = true;
                this.updateFarm(farm)
                    .then(response => {
                        if (response.status == 200) {
                            this.editFarmAlert = {
                                message: "farm configuration updated",
                                type: "success",
                            }
                            this.upgrade = false;
                            this.showUpgradeConfirmation = false;
                        } else {
                            this.editFarmAlert = {
                                message: response.data['error'],
                                type: "error",
                            }
                        }
                        setTimeout(() => {
                            this.editFarmAlert = undefined
                        }, 2000)
                    }).catch(err => {
                        var msg = "server error"
                        if (err.response) {
                            // The request was made and the server responded with a status code
                            // that falls out of the range of 2xx
                            msg = err.response.data['error'] ? err.response.data['error'] : "server error"
                        }
                        this.editFarmAlert = {
                            message: msg,
                            type: "error",
                        }
                        setTimeout(() => {
                            this.editFarmAlert = undefined
                        }, 15000)
                    })
            },
            initialiseRefresh() {
                const that = this;
                this.refreshInterval = setInterval(() => {
                    that.getFarms();
                }, 60000)
            },
            isLoggedIn() {
                return Boolean(this.user.id)
            },
            refreshFarms() {
                clearInterval(this.refreshInterval);
                this.getFarms();
                this.initialiseRefresh();
            },
            viewNodes(item) {
                this.getNodes(item.id);
                this.setCustomPricesList(item.id)
                this.farmSelected = item;
                this.setFarm(item);
                this.farm_price = item.farm_cloudunits_price && Object.assign(this.farm_price, item.farm_cloudunits_price) || { cu: item.explorer_prices.cu, su: item.explorer_prices.su, ipv4u: item.explorer_prices.ipv4u };
            },
            viewSettings(farm) {
                this.farmToEdit = farm;
                this.settingsDialog = true;
            },
            getColor(status) {
                if (status === "Active") return "green";
                else return "red";
            },
            addFarm() {
                var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
                if (!this.newFarm.name) {
                    this.nameError.push("Please select a country.");
                    return;
                }
                if (!this.newFarm.email) {
                    this.mailError.push("Please enter a email.");
                    return;
                }
                if (!re.test(this.newFarm.email)) {
                    this.mailError.push("Please enter a valid email.");
                    return;
                }


                this.registerFarm(this.newFarm).then(response => {
                    if (response.data) {
                        this.newFarmAlert = {
                            message: "farm created",
                            type: "success",
                        }
                        // update in memory farms
                        this.getFarms();
                    } else {
                        this.newFarmAlert = {
                            message: response.data['error'],
                            type: "error",
                        }
                    }
                    setTimeout(() => {
                        this.editFarmAlert = undefined
                        this.addFarmDialog = false;
                    }, 2000)
                }).catch(err => {
                    var msg = "server error"
                    if (err.response) {
                        // The request was made and the server responded with a status code
                        // that falls out of the range of 2xx
                        msg = err.response.data['error'] ? err.response.data['error'] : "server error"
                    }
                    this.newFarmAlert = {
                        message: msg,
                        type: "error",
                    }
                })

            },
            setPlace(event) {
                this.newFarm.location.latitude = event.latLng.lat();
                this.newFarm.location.longitude = event.latLng.lng();
                console.log(this.newFarm);
            },
            addWallet(farm) {
                farm.wallet_addresses.push({ 'asset': 'TFT', address: '' })
            },
            removeWallet(farm, i) {
                farm.wallet_addresses.splice(i, 1)
            },
            cancelEditFarm() {
                this.settingsDialog = false;
            },
            expand(item) {
                if (this.expanded.includes(item)) {
                    this.expanded = this.expanded.filter(x => x.node_id !== item.node_id);
                } else {
                    this.expanded.push(item);
                }
            },
            goToEdit(farm) {
                this.$router.history.push(`/edit/${farm.id}`)
            },
            setFarmPrice(cu, su, ipv4u) {
                let prices = { cu: cu, su: su, ipv4u: ipv4u }
                let farmCustomPricesInfo = { farmId: this.farmSelected.id, prices: prices }
                this.setDefaultFarmPrices(farmCustomPricesInfo)
                    .then(response => {
                        this.showSetFarmPrice = false;
                        this.getFarms();
                    }).catch(err => {
                        console.log(err)
                    })
            },
            addCustomPrice(threebotName, cu, su, ipv4u) {
                if (this.$refs.customPriceForm.validate()) {
                    let prices = { cu: +cu, su: +su, ipv4u: +ipv4u }
                    let farmCustomPricesInfo = { farmId: this.farmSelected.id, prices: prices, threebotName: threebotName }
                    this.createOrUpdateFarmThreebotCustomPrice(farmCustomPricesInfo)
                        .then(response => {
                            this.openAddCustomModel = false;
                            this.setCustomPricesList(farmCustomPricesInfo.farmId);
                            this.customPrice = {
                                threebotName: '',
                                cu: null,
                                su: null,
                                ipv4u: null,
                                threebotId: null
                            };
                            this.addCustomModelError = null;
                            this.$refs.customPriceForm.resetValidation();
                        }).catch(err => {
                            console.log("Error: ", err.response.data.error)
                            this.addCustomModelError = err.response.data.error
                        })
                }
            },
        }
    });
});

function getCountries(){
return  [
    "Afghanistan",
    "Albania",
    "Algeria",
    "Andorra",
    "Angola",
    "Antigua and Barbuda",
    "Argentina",
    "Armenia",
    "Australia",
    "Austria",
    "Azerbaijan",
    "The Bahamas",
    "Bahrain",
    "Bangladesh",
    "Barbados",
    "Belarus",
    "Belgium",
    "Belize",
    "Benin",
    "Bhutan",
    "Bolivia",
    "Bosnia and Herzegovina",
    "Botswana",
    "Brazil",
    "Brunei",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Cabo Verde",
    "Cambodia",
    "Cameroon",
    "Canada",
    "Central African Republic",
    "Chad",
    "Chile",
    "China",
    "Colombia",
    "Comoros",
    "Congo, Democratic Republic of the",
    "Congo, Republic of the",
    "Costa Rica",
    "Côte d’Ivoire",
    "Croatia",
    "Cuba",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Djibouti",
    "Dominica",
    "Dominican Republic",
    "East Timor (Timor-Leste)",
    "Ecuador",
    "Egypt",
    "El Salvador",
    "Equatorial Guinea",
    "Eritrea",
    "Estonia",
    "Eswatini",
    "Ethiopia",
    "Fiji",
    "Finland",
    "France",
    "Gabon",
    "The Gambia",
    "Georgia",
    "Germany",
    "Ghana",
    "Greece",
    "Grenada",
    "Guatemala",
    "Guinea",
    "Guinea-Bissau",
    "Guyana",
    "Haiti",
    "Honduras",
    "Hungary",
    "Iceland",
    "India",
    "Indonesia",
    "Iran",
    "Iraq",
    "Ireland",
    "Israel",
    "Italy",
    "Jamaica",
    "Japan",
    "Jordan",
    "Kazakhstan",
    "Kenya",
    "Kiribati",
    "Korea, North",
    "Korea, South",
    "Kosovo",
    "Kuwait",
    "Kyrgyzstan",
    "Laos",
    "Latvia",
    "Lebanon",
    "Lesotho",
    "Liberia",
    "Libya",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Madagascar",
    "Malawi",
    "Malaysia",
    "Maldives",
    "Mali",
    "Malta",
    "Marshall Islands",
    "Mauritania",
    "Mauritius",
    "Mexico",
    "Micronesia, Federated States of",
    "Moldova",
    "Monaco",
    "Mongolia",
    "Montenegro",
    "Morocco",
    "Mozambique",
    "Myanmar (Burma)",
    "Namibia",
    "Nauru",
    "Nepal",
    "Netherlands",
    "New Zealand",
    "Nicaragua",
    "Niger",
    "Nigeria",
    "North Macedonia",
    "Norway",
    "Oman",
    "Pakistan",
    "Palau",
    "Panama",
    "Papua New Guinea",
    "Paraguay",
    "Peru",
    "Philippines",
    "Poland",
    "Portugal",
    "Qatar",
    "Romania",
    "Russia",
    "Rwanda",
    "Saint Kitts and Nevis",
    "Saint Lucia",
    "Saint Vincent and the Grenadines",
    "Samoa",
    "San Marino",
    "Sao Tome and Principe",
    "Saudi Arabia",
    "Senegal",
    "Serbia",
    "Seychelles",
    "Sierra Leone",
    "Singapore",
    "Slovakia",
    "Slovenia",
    "Solomon Islands",
    "Somalia",
    "South Africa",
    "Spain",
    "Sri Lanka",
    "Sudan",
    "Sudan, South",
    "Suriname",
    "Sweden",
    "Switzerland",
    "Syria",
    "Taiwan",
    "Tajikistan",
    "Tanzania",
    "Thailand",
    "Togo",
    "Tonga",
    "Trinidad and Tobago",
    "Tunisia",
    "Turkey",
    "Turkmenistan",
    "Tuvalu",
    "Uganda",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom",
    "United States",
    "Uruguay",
    "Uzbekistan",
    "Vanuatu",
    "Vatican City",
    "Venezuela",
    "Vietnam",
    "Yemen",
    "Zambia",
    "Zimbabwe"
]
}
