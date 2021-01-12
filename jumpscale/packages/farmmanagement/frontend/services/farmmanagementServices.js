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
    return axios.post(`${tfgridUrl}/farms`, farm);
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
    return axios.get(`${tfgridUrl}/nodes`, {
      params: {
        farm: farm_id
      }
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
  }
};
