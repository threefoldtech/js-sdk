// const axios = require('axios')

const apiClient = {
  content: {
    get: (url) => {
      return axios({
        url: url
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
  explorers: {
    get: () => {
      return axios({
        url: "/actors/admin/get_explorer/"
      })
    },
  },
  solutions: {
    getDeployed: () => {
      return axios({
        url: `/threebot_deployer/api/threebots/list`,
        method: "get",
        headers: { 'Content-Type': 'application/json' }
      })
    },
    getAllThreebots: () => {
      return axios({
        url: `/threebot_deployer/api/threebots/list-all`,
        method: "get",
        headers: { 'Content-Type': 'application/json' }
      })

    },
    cancelReservation: (wids) => {
      return axios({
        url: `/threebot_deployer/api/solutions/cancel`,
        headers: { 'Content-Type': 'application/json' },
        data: { wids: wids },
        method: "post"
      })
    },
    stopThreebot: (uuid, password) => {
      return axios({
        url: `/threebot_deployer/api/threebots/stop`,
        headers: { 'Content-Type': 'application/json' },
        data: { uuid: uuid , password: password },
        method: "post"
      })
    },
    destroyThreebot: (uuid, password) => {
      return axios({
        url: `/threebot_deployer/api/threebots/destroy`,
        headers: { 'Content-Type': 'application/json' },
        data: { uuid: uuid, password: password },
        method: "post"
      })
    },
    destroyBackup: (threebotName) => {
      return axios({
        url: `/threebot_deployer/backup/destroy`,
        headers: { 'Content-Type': 'application/json' },
        data: { "threebot_name": threebotName },
        method: "post"
      })
    },
  },
  license: {
    accept: () => {
      return axios({
        url: `/threebot_deployer/api/accept/`,
        method: "get"
      })
    },
  }
}
