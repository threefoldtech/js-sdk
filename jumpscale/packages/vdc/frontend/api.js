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
    getAllThreebots: () => {
      return axios({
        url: `/vdc/api/threebots/list`,
        method: "get",
        headers: { 'Content-Type': 'application/json' }
      })

    },
    stopThreebot: (uuid, password) => {
      return axios({
        url: `/vdc/api/threebots/stop`,
        headers: { 'Content-Type': 'application/json' },
        data: { uuid: uuid , password: password },
        method: "post"
      })
    },
    destroyThreebot: (uuid, password) => {
      return axios({
        url: `/vdc/api/threebots/destroy`,
        headers: { 'Content-Type': 'application/json' },
        data: { uuid: uuid, password: password },
        method: "post"
      })
    },
  },
  license: {
    accept: () => {
      return axios({
        url: `/vdc/api/accept/`,
        method: "get"
      })
    },
  }
}
