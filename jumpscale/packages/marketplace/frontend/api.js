// const axios = require('axios')

const apiClient = {
  admins: {
    getCurrentUser: () => {
      return axios({
        url: "/auth/authenticated/"
      })
    }
  },
  explorers: {
    get: () => {
      return axios({
        url: "/actors/admin/get_explorer"
      })
    },
  },
  solutions: {
    getCount: () => {
      return axios({
        url: "/tfgrid_solutions/actors/solutions/count_solutions"
      })
    },
    getDeployed: (solution_type) => {
      return axios({
        url: `/marketplace/api/solutions/${solution_type}/`,
        method: "get",
        headers: {'Content-Type': 'application/json'}
      })
    }
  }
}
