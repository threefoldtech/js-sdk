// const axios = require('axios')
const baseURL = "/marketplacevdc/actors"

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
  solutions: {
    getCount: () => {
      return axios({
        url: "/marketplacevdc/api/solutions/count/",
        method: "get"
      })
    },
    getSolutions: (solutionType) => {
      return axios({
        url: `${baseURL}/solutions/list_solutions`, // TODO Replace with bottle server api call
        method: "post",
        data: { solution_type: solutionType },
        headers: { 'Content-Type': 'application/json' }
      })
    },
    deleteSolution: (releaseName, solutionId) => {
      return axios({
        url: `${baseURL}/chart/uninstall_helm_chart`, // TODO Replace with bottle server api call
        method: "post",
        data: { release: releaseName , solution_id: solutionId},
        headers: { 'Content-Type': 'application/json' }
      })
    },
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
