import tfService from "../services/farmmanagementServices.js";
import lodash from "/weblibs/lodash/lodash.min.js";

export default {
    namespaced: true,

    state: {
        user: {},
        tfgridUrl: null,
        nodes: [],
        farms: [],
        farm: {},
        nodeSpecs: {
            amountregisteredNodes: 0,
            amountregisteredFarms: 0,
            countries: 0,
            onlinenodes: 0,
            cru: 0,
            mru: 0,
            sru: 0,
            hru: 0
        },
        customPricesList: [{ id: "50", name: "samar", cu: 32, su: 43, ip4u: 9 },
            { id: "57", name: "sara", cu: 87, su: 45, ip4u: 54 },
            { id: "89", name: "ehab", cu: 23, su: 34, ip4u: 68 },
            { id: "32", name: "thabet", cu: 12, su: 46, ip4u: 76 },
        ],
        currentCustomPrice: null,
        explorerPrices: { cu: 0, su: 0, ipv4u: 0 }
    },
    actions: {
        getTfgridUrl: async context => {
            var response = await tfService.getExplorer();
            var url = JSON.parse(response.data).url
            context.commit("setTfgridUrl", url);
        },
        getUser: async context => {
            var response = await tfService.getUser();
            var user = JSON.parse(response.data)
            if (user.name.length > 0) {
                context.commit("setUser", user);
            }
        },
        getNodes(context, farm_id) {
            tfService.getNodes(context.getters.tfgridUrl, farm_id).then(response => {
                context.commit("setNodes", JSON.parse(response.data));
                context.commit("setTotalSpecs", JSON.parse(response.data));
            });
        },
        setNodeFree(context, { node_id, free }) {
            return tfService.setNodeFree(node_id, free)
        },
        getFarms: context => {
            tfService.getFarms(context.getters.user.id).then(response => {
                context.commit("setFarms", JSON.parse(response.data));
            });
        },
        getFarm(context, farm_id) {
            tfService.getFarm(farm_id).then(response => {
                context.commit("setFarm", JSON.parse(response.data));
            });
        },
        registerFarm: (context, farm) => {
            return tfService.registerFarm(context.getters.tfgridUrl, farm)
        },
        updateFarm(context, farm) {
            return tfService.updateFarm(farm.id, farm);
        },
        deleteIpAddress(context, toDel) {
            return tfService.removePublicIPs(toDel.farm_id, [toDel.ipaddress])
        },
        createIpAddress(context, toInsert) {
            return tfService.addPublicIPs(toInsert.farm_id, [{
                address: toInsert.address,
                gateway: toInsert.gateway
            }])
        },
        deleteNodeFarm(context, node) {
            return tfService.deleteNodeFarm(node)
        },
        getCustomPrices(context, farmId) {
            return tfService.getCustomPrices(farmId)
        },
        createOrUpdateFarmThreebotCustomPrice(context, createCustomPriceForThreebotInfo) {
            console.log(createCustomPriceForThreebotInfo)
            let farmId = createCustomPriceForThreebotInfo.farmId
            let threebotId = createCustomPriceForThreebotInfo.threebotId
            let prices = createCustomPriceForThreebotInfo.prices
            return tfService.createOrUpdateFarmThreebotCustomPrice(farmId, threebotId, prices)
        },
        setDefaultCustomPrices(context, farmDefaultCustomPricesInfo) {
            let farmId = farmDefaultCustomPricesInfo.farmId
            let prices = farmDefaultCustomPricesInfo.prices
            console.log(farmId, prices, 'storeeee');
            return tfService.setDefaultCustomPrices(farmId, prices)
        },
        setCustomPricesList(context, farmId) {
            tfService.getCustomPrices(farmId).then(response => {
                context.commit("setCustomPricesList", JSON.parse(response.data))
            })
        },
    },

    mutations: {
        setCustomPricesList(state, pricesList) {
            state.customPricesList = pricesList
        },
        setFarms(state, value) {
            state.farms = value;
        },
        setFarm(state, value) {
            state.farm = value
        },
        setNodes(state, value) {
            state.nodes = value;
        },
        setUser: (state, user) => {
            state.user = user;
        },
        setTfgridUrl: (state, tfgridUrl) => {
            state.tfgridUrl = tfgridUrl;
        },
        setAmountOfFarms(state, value) {
            state.nodeSpecs.amountregisteredFarms = value.length;
        },
        setTotalSpecs(state, value) {
            state.nodeSpecs.amountregisteredNodes = value.length;
            state.nodeSpecs.onlinenodes = countOnlineNodes(value);
            state.nodeSpecs.countries = lodash.uniqBy(
                value,
                node => node.location.country
            ).length;
            state.nodeSpecs.cru = lodash.sumBy(
                value,
                node => node.total_resources.cru
            );
            state.nodeSpecs.mru = lodash.sumBy(
                value,
                node => node.total_resources.mru
            );
            state.nodeSpecs.sru = lodash.sumBy(
                value,
                node => node.total_resources.sru
            );
            state.nodeSpecs.hru = lodash.sumBy(
                value,
                node => node.total_resources.hru
            );
        },
    },

    getters: {
        user: state => state.user,
        tfgridUrl: state => state.tfgridUrl,
        nodes: state => state.nodes,
        farms: state => state.farms,
        farm: state => state.farm,
        nodeSpecs: state => state.nodeSpecs,
        freeSwitchAlert: state => state.freeSwitchAlert,
        customPricesList: state => state.customPricesList,
    }
};

function countOnlineNodes(data) {
    let onlinecounter = 0;
    data.forEach(node => {
        const timestamp = new Date().getTime() / 1000;
        const minutes = (timestamp - node.updated) / 60;
        if (minutes < 20) onlinecounter++;
    });
    return onlinecounter;
}