module.exports = new Promise(async (resolve, reject) => {
    const vuex = await import(
        "/weblibs/vuex/vuex.esm.browser.js"
    )
    const ipaddr = await import("https://cdn.jsdelivr.net/npm/ip-address@5.8.9/dist/ip-address-globals.js")

    resolve({
        name: "farmedit",
        data() {
            return {
                countries,
                editFarmAlert: undefined,
                headers: [
                    { text: "IP Address", value: "address" },
                    { text: "Gateway IP", value: "gateway" },
                    { text: "Reservation ID", value: "reservation_id" },
                    { text: "Actions", value: "action", sortable: false }
                ],
                openDeleteModal: false,
                openCreateModal: false,
                newIpAddress: {
                    ipaddress: '',
                    gatewayIP: ''
                },
                newIpAddressError: '',
                rules: {
                    required: value => !!value || 'Required.',
                    validIp: value => new window.Address4(value).isValid(),
                    length: value => value.length == 56 || 'Invalid wallet',
                },
            }
        },
        async mounted() {
            await this.getFarm(this.$router.history.current.params.id)
        },
        methods: {
            ...vuex.mapActions("farmmanagement", [
                "getFarm",
                "updateFarm",
                "deleteIpAddress",
                "createIpAddress",
                "addIpAddress"
            ]),
            saveFarm(goBack) {
                this.updateFarm(this.farm)
                    .then(response => {
                        if (response.status == 200) {
                            this.editFarmAlert = {
                                message: "farm configuration updated",
                                type: "success",
                            }
                            this.getFarm(this.$router.history.current.params.id)
                        } else {
                            this.editFarmAlert = {
                                message: response.data['error'],
                                type: "error",
                            }
                        }
                        setTimeout(() => {
                            this.editFarmAlert = undefined
                        }, 2000)
                        if (goBack) this.$router.push('/')
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
            addWallet(farm) {
                farm.wallet_addresses.push({ 'asset': 'TFT', address: '' })
            },
            removeWallet(farm, i) {
                farm.wallet_addresses.splice(i, 1)
            },
            cancelEditFarm() {
                this.$router.push('/')
            },
            deleteIpAddressFarmer(ipaddress) {
                const del = {
                    farm_id: this.farm.id,
                    ipaddress: ipaddress.address
                }
                this.deleteIpAddress(del)
                    .then(response => {
                        if (response.status == 200) {
                            this.editFarmAlert = {
                                message: "farm configuration updated",
                                type: "success",
                            }
                            this.getFarm(this.$router.history.current.params.id)
                        } else {
                            this.editFarmAlert = {
                                message: response.data['error'],
                                type: "error",
                            }
                        }
                        this.editFarmAlert = undefined
                        this.openDeleteModal = false
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
                        }, 2500)
                        this.openDeleteModal = false
                    })
            },
            createIpAddressFarmer() {
                const insert = {
                    farm_id: this.farm.id,
                    address: this.newIpAddress.ipaddress,
                    gateway: this.newIpAddress.gatewayIP
                }
                this.createIpAddress(insert)
                    .then(response => {
                        if (response.status == 200) {
                            this.editFarmAlert = {
                                message: "farm configuration updated",
                                type: "success",
                            }
                            this.getFarm(this.$router.history.current.params.id)
                        } else {
                            this.editFarmAlert = {
                                message: response.data['error'],
                                type: "error",
                            }
                        }
                        this.editFarmAlert = undefined
                        this.openCreateModal = false
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
                        }, 2500)
                        this.openCreateModal = false
                    })
            }
        },
        computed: {
            ...vuex.mapGetters("farmmanagement", ["farm"]),
        },
    })
})

const countries = [
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
