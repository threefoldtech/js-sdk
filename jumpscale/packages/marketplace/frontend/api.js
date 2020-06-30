// const axios = require('axios')

const apiClient = {
  logs: {
    listApps: () => {
      return axios({
        url: "/actors/logs/list_apps",
        method: "post"
      })
    },
    listLogs: (appname) => {
      return axios({
        url: "/actors/logs/list_logs",
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: { appname: appname }
      })
    }
  },
  alerts: {
    listAlerts: () => {
      return axios({
        url: "/actors/alerts/list_alerts",
        method: "post",
        headers: {'Content-Type': 'application/json'}
      })
    }
  },
  wallets: {
    list: () => {
      return axios({
        url: "/actors/wallet/get_wallets",
        method: "post",
        headers: {'Content-Type': 'application/json'}
      })
    },
    get: (name) => {
      return axios({
        url: "/actors/wallet/get_wallet_info",
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: {name: name}
      })
    },
    create: (name) => {
      return axios({
        url: "/actors/wallet/create_wallet",
        method: "post",
        data: {name: name}
      })
    },
    import: (name, secret, network) => {
      return axios({
        url: "/actors/wallet/import_wallet",
        method: "post",
        data: {name: name, secret: secret, network: network}
      })
    },
    delete: (name) => {
      return axios({
        url: "/actors/wallet/delete_wallet",
        method: "post",
        data: {name: name}
      })
    }
  },
  packages: {
    list: () => {
      return axios({
        url: "/actors/packages/list_packages"
      })
    },
    add: (path, giturl) => {
      return axios({
        url: "/actors/packages/add_package",
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: {path: path, giturl: giturl}
      })
    },
    delete: (name) => {
      return axios({
        url: "/actors/packages/delete_package",
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: {name: name}
      })
    },
    getInstalled: () => {
      return axios({
        url: "/actors/packages/packages_names"
      })
    }
  },
  admins: {
    list: () => {
      return axios({
        url: "/actors/admin/list_admins"
      })
    },
    add: (name) => {
      return axios({
        url: "/actors/admin/add_admin",
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: {name: name}
      })
    },
    remove: (name) => {
      return axios({
        url: "/actors/admin/delete_admin",
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: {name: name}
      })
    },
    getCurrentUser: () => {
      return axios({
        url: "/actors/admin/get_current_user"
      })
    },
    getIdentity: () => {
      return axios({
        url: "/actors/health/get_identity"
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
        url: "/tfgrid_solutions/actors/solutions/list_solutions",
        method: "post",
        headers: {'Content-Type': 'application/json'},
        data: {solution_type: solution_type}
      })
    }
  },
  health: {
    getMemoryUsage () {
      return axios({
        url: "/actors/health/get_memory_usage"
      })
    },
    getDiskUsage () {
      return axios({
        url: "/actors/health/get_disk_space"
      })
    },
    getRunningProcesses () {
      return axios({
        url: "/actors/health/get_running_processes"
      })
    }
  }
}
