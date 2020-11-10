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
    getCount: () => {
      return axios({
        url: "/marketplace/api/solutions/count/",
        method: "get"
      })
    },
    getDeployed: (solutionType) => {
      return axios({
        url: `/marketplace/api/solutions/${solutionType}/`,
        method: "get",
        headers: { 'Content-Type': 'application/json' }
      })
    },
    cancelReservation: (wids) => {
      return axios({
        url: `/marketplace/api/solutions/cancel`,
        headers: { 'Content-Type': 'application/json' },
        data: { wids: wids },
        method: "post"
      })
    }
  },
  license: {
    accept: () => {
      return axios({
        url: `/marketplace/api/accept/`,
        method: "get"
      })
    },
  }
}
