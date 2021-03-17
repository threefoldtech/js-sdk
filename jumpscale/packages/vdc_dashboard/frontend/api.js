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
    getVdcInfo: () => {
      return axios({
        url: `${baseURL}/threebot_vdc`,
        headers: { 'Content-Type': 'application/json' },
        method: "get"
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
    deleteWorkerWorkload: (wid) => {
      return axios({
        url: `${baseURL}/kube/nodes/delete`,
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
    delete: (name) => {
      return axios({
        url: `${baseURL}/backup/delete`,
        method: "post",
        data: { name: name },
        headers: { 'Content-Type': 'application/json' }
      })
    },
    restore: (name) => {
      return axios({
        url: `${baseURL}/backup/restore`,
        method: "post",
        data: { name: name },
        headers: { 'Content-Type': 'application/json' }
      })
    },
  },
  quantumstorage: {
    enable: () => {
      return axios({
        url: `${baseURL}/quantumstorage/enable`,
        headers: { 'Content-Type': 'application/json' },
        method: "get"
      })
    }
  }
}
