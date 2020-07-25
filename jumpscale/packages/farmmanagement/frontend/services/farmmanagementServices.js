import axios from "/weblibs/axios/axios.min.js";

export default {
  getExplorer() {
    return axios.get("/admin/actors/admin/get_explorer");
  },
  getUser() {
    return axios.get("/auth/authenticated");
  },
  getFarms(tfgridUrl, user_id) {
    return axios.get(`${tfgridUrl}/farms`, {
      params: {
        owner: user_id
      }
    });
  },
  registerFarm(tfgridUrl, farm) {
    return axios.post(`${tfgridUrl}/farms`, farm);
  },
  updateFarm(farm_id, farm) {
    return axios.post('/farmmanagement/actors/farm_management/update_farm', {
      args: {
        farm_id: farm_id,
        farm: farm,
      }
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
    console.log(node_id, free)
    return axios.post('/farmmanagement/actors/farm_management/mark_node_free', {
      args: {
        node_id: node_id,
        free: free,
      }
    })
  }
};
