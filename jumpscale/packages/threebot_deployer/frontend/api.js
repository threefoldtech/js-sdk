// const axios = require('axios')

const apiClient = {
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
    getCount: () => {
      return axios({
        url: "/threebot_deployer/api/solutions/count/",
        method: "get"
      })
    },
    getDeployed: () => {
      return axios({
        url: `/threebot_deployer/api/threebots/list`,
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
    }
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
