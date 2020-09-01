import tfService from "../services/farmmanagementServices.js";
import lodash from "/weblibs/lodash/lodash.min.js";

export default {
  namespaced: true,

  state: {
    user: {},
    tfgridUrl: null,
    nodes: [],
    farms: [],
    nodeSpecs: {
      amountregisteredNodes: 0,
      amountregisteredFarms: 0,
      countries: 0,
      onlinenodes: 0,
      cru: 0,
      mru: 0,
      sru: 0,
      hru: 0
    }
  },
  actions: {
    getTfgridUrl: async context => {
      const response = await tfService.getExplorer()
      let url = JSON.parse(response.data).data.url
      // Temporary fix.
      // This should be reverted when capacity pool goes live on mainnet.
      if (!url.startsWith('http') && !url.includes("testnet")) {
        url = `https://${url}/explorer`
      } else {
        url = `https://${url}/api/v1`
      }
      context.commit("setTfgridUrl", url)
    },
    getUser: async context => {
      var response = await tfService.getUser();
      if (response.data.username.length > 0) {
        context.commit("setUser", response.data);
      }
    },
    getNodes(context, farm_id) {
      tfService.getNodes(context.getters.tfgridUrl, farm_id).then(response => {
        context.commit("setNodes", response.data);
        context.commit("setTotalSpecs", response.data);
      });
    },
    setNodeFree(context, { node_id, free }) {
      return tfService.setNodeFree(node_id, free)
    },
    getFarms: context => {
      tfService.getFarms(context.getters.tfgridUrl, context.getters.user.tid).then(response => {
        context.commit("setFarms", response.data);
      });
    },
    registerFarm: (context, farm) => {
      return tfService.registerFarm(context.getters.tfgridUrl, farm)
    },
    updateFarm(context, farm) {
      return tfService.updateFarm(farm.id, farm);
    },
    deleteNodeFarm(context, node) {
      return tfService.deleteNodeFarm(node)
    }
  },
  mutations: {
    setFarms(state, value) {
      state.farms = value;
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
    }
  },

  getters: {
    user: state => state.user,
    tfgridUrl: state => state.tfgridUrl,
    nodes: state => state.nodes,
    farms: state => state.farms,
    nodeSpecs: state => state.nodeSpecs,
    freeSwitchAlert: state => state.freeSwitchAlert
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
