// const axios = require('axios')
const baseURL = "/vdc_dashboard/api"

const apiClient = {
  content: {
    get: (url) => {
      return axios({
        url: url
      })
    }
  },
  server: {
    isRunning: () => {
      return axios({
        url: `${baseURL}/vdc/status`,
        method: "get"
      })
    }
  },
  admins: {
    getCurrentUser: () => {
      return axios({
        url: "/auth/authenticated/"
      })
    },
    list: () => {
      return axios({
        url: `${baseURL}/admins/list`
      })
    },
    add: (name) => {
      return axios({
        url: `${baseURL}/admins/add`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { name: name }
      })
    },
    remove: (name) => {
      return axios({
        url: `${baseURL}/admins/remove`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { name: name }
      })
    }
  },
  vdc: {
    getVdcInfo: () => {
      return axios({
        url: `${baseURL}/vdc/info`,
        headers: { 'Content-Type': 'application/json' },
        method: "get"
      })
    },
    getVdcExpiration: () => {
      return axios({
        url: `${baseURL}/vdc/expiration`,
        headers: { 'Content-Type': 'application/json' },
        method: "get"
      })
    },
    getVdcPlanPrice: () => {
      return axios({
        url: `${baseURL}/vdc/plan/price`,
        headers: { 'Content-Type': 'application/json' },
        method: "get"
      })
    },
    checkVdcPlanAutoscalable: () => {
      return axios({
        url: `${baseURL}/vdc/plan/autoscalable`,
        headers: { 'Content-Type': 'application/json' },
        method: "get"
      })
    },
    getVdcWalletInfo: () => {
      return axios({
        url: `${baseURL}/vdc/wallet`,
        headers: { 'Content-Type': 'application/json' },
        method: "get"
      })
    },
  },
  solutions: {
    getSolutions: (solutionType) => {
      return axios({
        url: `${baseURL}/deployments/${solutionType}`,
        method: "get",
      })
    },
    getAllSolutions: (solutionTypes) => {
      return axios({
        url: `${baseURL}/deployments`,
        method: "post",
        data: { solution_types: solutionTypes },
        headers: { 'Content-Type': 'application/json' }
      })
    },
    deleteSolution: (releaseName, solutionId, vdcName, namespace) => {
      return axios({
        url: `${baseURL}/deployments/cancel/`,
        method: "post",
        data: { release: releaseName, solution_id: solutionId, vdc_name: vdcName, namespace: namespace },
        headers: { 'Content-Type': 'application/json' }
      })
    },
    exposeS3: () => {
      return axios({
        url: `${baseURL}/s3/expose`,
        headers: { 'Content-Type': 'application/json' },
        method: "get"
      })
    },
    getKubeConfig: () => {
      return axios({
        url: `${baseURL}/kube/get`,
        headers: { 'Content-Type': 'application/json' },
        method: "get"
      })
    },
    getThreebotState: () => {
      return axios({
        url: `${baseURL}/threebot/export`,
        headers: { 'Content-Type': 'application/json' },
        responseType: 'arraybuffer',
        method: "get"
      })
    },
    getVMs: () => {
      return axios({
        url: `${baseURL}/vmachine`,
        method: "get",
        headers: { 'Content-Type': 'application/json' }
      })
    },
    deleteVm: (wid) => {
      return axios({
        url: `${baseURL}/vmachine`,
        method: "delete",
        data: { wid: wid },
        headers: { 'Content-Type': 'application/json' }
      })
    },
    deleteWorkerWorkload: (wid, releasesToDelete) => {
      return axios({
        url: `${baseURL}/kube/nodes/delete`,
        method: "post",
        data: { wid: wid, releases_to_delete: releasesToDelete },
        headers: { 'Content-Type': 'application/json' }
      })
    },
    checkBeforeDeleteWorkerWorkload: (wid) => {
      return axios({
        url: `${baseURL}/kube/nodes/check_before_delete`,
        method: "post",
        data: { wid: wid },
        headers: { 'Content-Type': 'application/json' }
      })
    },
    deleteZdb: (wid) => {
      return axios({
        url: `${baseURL}/s3/zdbs/delete`,
        method: "post",
        data: { wid: wid },
        headers: { 'Content-Type': 'application/json' }
      })
    },
    getZstorConfig: (ip_version) => {
      return axios({
        url: `${baseURL}/zstor/config`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { ip_version: ip_version }
      })
    },
    getZdbSecret: () => {
      return axios({
        url: `${baseURL}/zdb/secret`,
        method: "get",
        headers: { 'Content-Type': 'application/json' }
      })
    },
    redeployMaster: (wid) => {
      return axios({
        url: `${baseURL}/redeploy_master`,
        method: "post",
        data: { wid: wid },
        headers: { 'Content-Type': 'application/json' }
      })
    },
  },
  license: {
    accept: () => {
      return axios({
        url: `${baseURL}/accept/`,
        method: "get"
      })
    },
  },
  version: {
    update: () => {
      return axios({
        url: `${baseURL}/update`,
        method: "get"
      })
    },
    checkForUpdate: () => {
      return axios({
        url: `${baseURL}/check_update`,
        method: "get"
      })
    },
    getSDKVersion: () => {
      return axios({
        url: `${baseURL}/get_sdk_version`
      })
    },
  },
  wallets: {
    walletQRCodeImage: (address, amount, scale) => {
      return axios({
        url: `${baseURL}/wallet/qrcode/get`,
        method: "post",
        data: { address: address, amount: amount, scale: scale },
        headers: { 'Content-Type': 'application/json' }
      })
    },
  },
  backup: {
    list: () => {
      return axios({
        url: `${baseURL}/backup/list`,
        headers: { 'Content-Type': 'application/json' }
      })
    },
    create: (name) => {
      return axios({
        url: `${baseURL}/backup/create`,
        method: "post",
        data: { name: name },
        headers: { 'Content-Type': 'application/json' }
      })
    },
    delete: (vdcBackup, configBackup) => {
      return axios({
        url: `${baseURL}/backup/delete`,
        method: "post",
        data: { vdc_backup_name: vdcBackup, config_backup_name: configBackup },
        headers: { 'Content-Type': 'application/json' }
      })
    },
    restore: (vdcBackup, configBackup) => {
      return axios({
        url: `${baseURL}/backup/restore`,
        method: "post",
        data: { vdc_backup_name: vdcBackup, config_backup_name: configBackup },
        headers: { 'Content-Type': 'application/json' }
      })
    },
  },
  alerts: {
    listAlerts: () => {
      return axios({
        url: `${baseURL}/alerts`,
        method: "get",
        headers: { 'Content-Type': 'application/json' }
      });
    }
  },
  quantumstorage: {
    enable: () => {
      return axios({
        url: `${baseURL}/quantumstorage/enable`,
        headers: { 'Content-Type': 'application/json' },
        method: "get"
      })
    }
  },
  apikeys: {
    list: () => {
      return axios({
        url: `${baseURL}/api_keys`
      })
    },
    generate: (name, role) => {
      return axios({
        url: `${baseURL}/api_keys`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { name: name, role: role }
      })
    },
    regenerate: (name) => {
      return axios({
        url: `${baseURL}/api_keys`,
        method: "put",
        headers: { 'Content-Type': 'application/json' },
        data: { name: name, regenerate: true }
      })
    },
    edit: (name, role) => {
      return axios({
        url: `${baseURL}/api_keys`,
        method: "put",
        headers: { 'Content-Type': 'application/json' },
        data: { name: name, role: role }
      })
    },
    delete: (name) => {
      return axios({
        url: `${baseURL}/api_keys`,
        method: "delete",
        headers: { 'Content-Type': 'application/json' },
        data: { name: name }
      })
    },
    deleteAll: () => {
      return axios({
        url: `${baseURL}/api_keys`,
        method: "delete",
        headers: { 'Content-Type': 'application/json' },
        data: { all: true }
      })
    },
  }
}
