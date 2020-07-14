// const axios = require('axios')
const baseURL = "/admin/actors"

const apiClient = {
  logs: {
    listApps: () => {
      return axios({
        url: `${baseURL}/logs/list_apps`,
        method: "post"
      })
    },
    listLogs: (appname) => {
      return axios({
        url: `${baseURL}/logs/list_logs`,
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: { appname: appname }
      })
    },
    delete: (appname) => {
      return axios({
        url: `${baseURL}/logs/remove_records`,
        method: "post",
        data: { appname: appname }
      })
    }
  },
  alerts: {
    listAlerts: () => {
      return axios({
        url: `${baseURL}/alerts/list_alerts`,
        method: "post",
        headers: {'Content-Type': 'application/json'}
      })
    },
    deleteAll: () => {
      return axios({
        url: `${baseURL}/alerts/delete_all_alerts`,
        method: "post",
      })
    }
  },
  wallets: {
    list: () => {
      return axios({
        url: `${baseURL}/wallet/get_wallets`,
        method: "post",
        headers: {'Content-Type': 'application/json'}
      })
    },
    get: (name) => {
      return axios({
        url: `${baseURL}/wallet/get_wallet_info`,
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: {name: name}
      })
    },
    create: (name) => {
      return axios({
        url: `${baseURL}/wallet/create_wallet`,
        method: "post",
        data: {name: name}
      })
    },
    import: (name, secret, network) => {
      return axios({
        url: `${baseURL}/wallet/import_wallet`,
        method: "post",
        data: { name: name, secret: secret, network: network }
      })
    },
    delete: (name) => {
      return axios({
        url: `${baseURL}/wallet/delete_wallet`,
        method: "post",
        data: {name: name}
      })
    }
  },
  packages: {
    list: () => {
      return axios({
        url: `${baseURL}/packages/list_packages`
      })
    },
    add: (path, giturl, extras) => {
      return axios({
        url: `${baseURL}/packages/add_package`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { path: path, giturl: giturl, extras: extras }
      })
    },
    delete: (name) => {
      return axios({
        url: `${baseURL}/packages/delete_package`,
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: {name: name}
      })
    },
    getInstalled: () => {
      return axios({
        url: `${baseURL}/packages/packages_names`
      })
    }
  },
  admins: {
    list: () => {
      return axios({
        url: `${baseURL}/admin/list_admins`
      })
    },
    add: (name) => {
      return axios({
        url: `${baseURL}/admin/add_admin`,
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: {name: name}
      })
    },
    remove: (name) => {
      return axios({
        url: `${baseURL}/admin/delete_admin`,
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: {name: name}
      })
    },
    getCurrentUser: () => {
      return axios({
        url: `${baseURL}/admin/get_current_user`
      })
    },
    getIdentity: () => {
      return axios({
        url: `${baseURL}/health/get_identity`
      })
    },
    setExplorer: (explorerType) => {
      return axios({
        url: `${baseURL}/admin/set_explorer`,
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: {explorer_type: explorerType}
      })
    }
  },
  explorers: {
    get: () => {
      return axios({
        url: `${baseURL}/admin/get_explorer`
      })
    },
  },
  solutions: {
    getCount: () => {
      return axios({
        url: `/tfgrid_solutions/actors/solutions/count_solutions`
      })
    },
    getDeployed: (solution_type) => {
      return axios({
        url: `/tfgrid_solutions/actors/solutions/list_solutions`,
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: {solution_type: solution_type}
      })
    },
    getAll: () => {
      return axios({
        url: `/tfgrid_solutions/actors/solutions/list_all_solutions`,
      })
    },
    cancelReservation: (solutionType, solutionName) => {
      return axios({
        url: `/tfgrid_solutions/actors/solutions/cancel_solution`,
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: {solution_type: solutionType, solution_name: solutionName}
      })
    }
  },
  health: {
    getMemoryUsage () {
      return axios({
        url: `${baseURL}/health/get_memory_usage`
      })
    },
    getDiskUsage () {
      return axios({
        url: `${baseURL}/health/get_disk_space`
      })
    },
    getRunningProcesses () {
      return axios({
        url: `${baseURL}/health/get_running_processes`
      })
    }
  }
}
