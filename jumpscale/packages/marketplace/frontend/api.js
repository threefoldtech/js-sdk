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
    cancelReservation: (solutionType, reservationId) => {
      return axios({
        url: `/marketplace/api/solutions/${solutionType}/${reservationId}/`,
        method: "delete"
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
