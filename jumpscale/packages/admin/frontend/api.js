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
        headers: { 'Content-Type': 'application/json' },
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
        headers: { 'Content-Type': 'application/json' }
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
        headers: { 'Content-Type': 'application/json' }
      })
    },
    get: (name) => {
      return axios({
        url: `${baseURL}/wallet/get_wallet_info`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { name: name }
      })
    },
    create: (name) => {
      return axios({
        url: `${baseURL}/wallet/create_wallet`,
        method: "post",
        data: { name: name }
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
        data: { name: name }
      })
    },
    updateTrustlines: (name) => {
      return axios({
        url: `${baseURL}/wallet/update_trustlines`,
        method: "post",
        data: { name: name }
      })
    },

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
        headers: { 'Content-Type': 'application/json' },
        data: { name: name }
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
        headers: { 'Content-Type': 'application/json' },
        data: { name: name }
      })
    },
    remove: (name) => {
      return axios({
        url: `${baseURL}/admin/delete_admin`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { name: name }
      })
    },
    getCurrentUser: () => {
      return axios({
        url: `/auth/authenticated/`
      })
    }
  },
  explorers: {
    get: () => {
      return axios({
        url: `${baseURL}/admin/get_explorer`
      })
    },
    list: () => {
      return axios({
        url: `${baseURL}/admin/list_explorers`
      })
    },
  },
  identities: {
    list: () => {
      return axios({
        url: `${baseURL}/admin/list_identities`
      })
    },
    add: (identity_instance_name, tname, email, words, explorer_type) => {
      return axios({
        url: `${baseURL}/admin/add_identity`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { identity_instance_name: identity_instance_name, tname: tname, email: email, words: words, explorer_type: explorer_type }
      })
    },
    setIdentity: (identity_instance_name) => {
      return axios({
        url: `${baseURL}/admin/set_identity`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { identity_instance_name: identity_instance_name }
      })
    },
    getIdentity: (identity_instance_name) => {
      return axios({
        url: `${baseURL}/admin/get_identity`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { identity_instance_name: identity_instance_name }
      })
    },
    deleteIdentity: (identity_instance_name) => {
      return axios({
        url: `${baseURL}/admin/delete_identity`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { identity_instance_name: identity_instance_name }
      })
    }
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
        headers: { 'Content-Type': 'application/json' },
        data: { solution_type: solution_type }
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
        headers: { 'Content-Type': 'application/json' },
        data: { solution_type: solutionType, solution_name: solutionName }
      })
    }
  },
  health: {
    getMemoryUsage() {
      return axios({
        url: `${baseURL}/health/get_memory_usage`
      })
    },
    getDiskUsage() {
      return axios({
        url: `${baseURL}/health/get_disk_space`
      })
    },
    getRunningProcesses() {
      return axios({
        url: `${baseURL}/health/get_running_processes`
      })
    }
  },
  mrktbackup: {
    inited() {
      return axios({
        url: `/backup/actors/marketplace/repos_exist`
      })
    },
    snapshots() {
      return axios({
        url: `/backup/actors/marketplace/snapshots`
      })
    },
    init(password) {
      return axios({
        url: `/backup/actors/marketplace/init`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { password: password }
      })
    },
    backup(tags) {
      return axios({
        url: `/backup/actors/marketplace/backup`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { tags: tags }
      })
    },
    enable: () => {
      return axios({
        url: `/backup/actors/marketplace/enable_auto_backup`
      })
    },
    disable() {
      return axios({
        url: `/backup/actors/marketplace/disable_auto_backup`
      })
    },
    enabled() {
      return axios({
        url: `/backup/actors/marketplace/check_auto_backup`
      })
    },
  },
  miniobackup: {
    inited() {
      return axios({
        url: `/backup/actors/minio/repos_exist`
      })
    },
    snapshots() {
      return axios({
        url: `/backup/actors/minio/snapshots`
      })
    },
    init(minio_url, password, access_key, secret_key) {
      return axios({
        url: `/backup/actors/minio/init`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { minio_url: minio_url, password: password, access_key: access_key, secret_key: secret_key }
      })
    },
    backup(tags) {
      return axios({
        url: `/backup/actors/minio/backup`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { tags: tags }
      })
    },
    enable: () => {
      return axios({
        url: `/backup/actors/minio/enable_auto_backup`
      })
    },
    disable() {
      return axios({
        url: `/backup/actors/minio/disable_auto_backup`
      })
    },
    enabled() {
      return axios({
        url: `/backup/actors/minio/check_auto_backup`
      })
    },
  },
  identity: {
    get: () => {
      return axios({
        url: `${baseURL}/identity/get_identity`
      })
    },
    list: () => {
      return axios({
        url: `${baseURL}/identity/list_identities`
      })
    },
    set: (label, tname, email, words, backup_password) => {
      return axios({
        url: `${baseURL}/identity/set_identity`,
        method: "post",
        headers: { 'Content-Type': 'application/json' },
        data: { label: label, tname: tname, email: email, words: words, backup_password: backup_password }
      })
    }
  },
  user: {
    currentUser: () => {
      return axios({
        url: "/auth/authenticated"
      })
    }
  }
}
