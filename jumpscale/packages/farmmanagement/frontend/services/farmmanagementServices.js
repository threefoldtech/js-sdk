import axios from "/weblibs/axios/axios.min.js";

export default {
    getExplorer() {
        return axios.get("/admin/actors/identity/get_explorer_url");
    },
    getUser() {
        return axios.get("/admin/actors/identity/get_identity");
    },
    getFarm(farm_id) {
        return axios.post('/farmmanagement/actors/farm_management/get_farm', {
            farm_id,
        })
    },
    getFarms(user_id) {
        return axios.post('/farmmanagement/actors/farm_management/list_farms', {
            user_id: user_id,
        })
    },
    registerFarm(tfgridUrl, farm) {
        return axios.post(`/farmmanagement/actors/farm_management/register_farm`, { farm: farm });
    },
    updateFarm(farm_id, farm) {
        return axios.post('/farmmanagement/actors/farm_management/update_farm', {
            farm_id: farm_id,
            farm: farm,
        })
    },
    deleteNodeFarm(node) {
        return axios.post('/farmmanagement/actors/farm_management/delete_node_farm', {
            farm_id: node.farmer.id,
            node_id: node.id,
        })
    },
    getNodes(tfgridUrl, farm_id = undefined) {
        return axios.post(`/farmmanagement/actors/farm_management/list_nodes`, {
            farm_id: farm_id
        })
    },
    setNodeFree(node_id, free) {
        return axios.post('/farmmanagement/actors/farm_management/mark_node_free', {
            node_id: node_id,
            free: free,
        })
    },
    addPublicIPs(farm_id, ip_addresses) {
        return axios.post('/farmmanagement/actors/farm_management/add_ip_addresses', {
            farm_id,
            ip_addresses,
        })
    },
    removePublicIPs(farm_id, ip_addresses) {
        return axios.post('/farmmanagement/actors/farm_management/remove_ip_addresses', {
            farm_id: farm_id,
            ip_addresses: ip_addresses,
        })
    },
    getCustomPrices(farmId) {
        console.log("FRM::" , farmId)
        return axios.post('/farmmanagement/actors/farm_management/get_deals_with_threebot_names', {
            farm_id: farmId
        })
    },
    setDefaultFarmPrices(farmId, prices) {
        return axios.post('/farmmanagement/actors/farm_management/enable_farm_default_prices', {
            farm_id: farmId,
            prices: prices,
        })
    },
    createOrUpdateFarmThreebotCustomPrice(farmId, threebotName, prices) {
        console.log('immed', farmId, threebotName, prices)
        return axios.post('/farmmanagement/actors/farm_management/create_or_update_deal_for_threebot_by_name', {
            farm_id: farmId,
            threebot_name: threebotName,
            custom_prices: prices,
        })

    },
    deleteDeal(farmId, threebotId) {
        return axios.post('/farmmanagement/actors/farm_management/delete_deal', {
            farm_id: farmId,
            threebot_id: threebotId,
        })
    },
    getExplorerPrices() {
        return axios.post('/farmmanagement/actors/farm_management/get_explorer_prices')
    },
};
