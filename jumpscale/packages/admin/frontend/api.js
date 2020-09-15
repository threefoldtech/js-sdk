// const axios = require('axios')
const baseURL = "/admin/actors"

const apiClient = {
    content: {
        get: (url) => {
            return axios({
                url: url
            })
        }
    },
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
        create_testnet_funded: (name) => {
            return axios({
                url: `${baseURL}/wallet/create_testnet_funded`,
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
        addInternal: (name, extras) => {
            return axios({
                url: `${baseURL}/packages/add_internal_package`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { name: name, extras: extras }
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
        },
        getDeveloperOptions: () => {
            return axios({
                url: `${baseURL}/admin/get_developer_options`
            })
        },
        setDeveloperOptions: (testCert, overProvision) => {
            return axios({
                url: `${baseURL}/admin/set_developer_options`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { test_cert: testCert, over_provision: overProvision }
            })
        },
        clearBlockedNodes: () => {
            return axios({
                url: `${baseURL}/admin/clear_blocked_nodes`,
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
        getPools: (include_hidden) => {
            return axios({
                method: "post",
                url: `/tfgrid_solutions/actors/solutions/list_pools`,
                data: {
                    include_hidden: include_hidden || false,
                }
            })
        },
        getAll: () => {
            return axios({
                url: `/tfgrid_solutions/actors/solutions/list_all_solutions`,
            })
        },
        cancelWorkload: (wid) => {
            return axios({
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                url: `/tfgrid_solutions/actors/solutions/cancel_workload`,
                data: { wid: wid }
            })
        },
        patchCancelWorkload: (wids) => {
            return axios({
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                url: `/tfgrid_solutions/actors/solutions/patch_cancel_workloads`,
                data: { wids: wids }
            })
        },
        cancelReservation: (wids) => {
            return axios({
                url: `/tfgrid_solutions/actors/solutions/cancel_solution`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { wids: wids }
            })
        },
        hasMigrated: () => {
            return axios({
                url: `/tfgrid_solutions/actors/solutions/has_migrated`,
            })
        },
        migrate: () => {
            return axios({
                url: `/tfgrid_solutions/actors/solutions/migrate`,
            })
        },
        hidePool: (pool_id) => {
            return axios({
                url: `/tfgrid_solutions/actors/solutions/hide_pool`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { pool_id: pool_id }
            })
        },
        renamePool: (pool_id, name) => {
            return axios({
                url: `/tfgrid_solutions/actors/solutions/rename_pool`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { pool_id: pool_id, name: name }
            })
        },
        unhidePool: (pool_id) => {
            return axios({
                url: `/tfgrid_solutions/actors/solutions/unhide_pool`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { pool_id: pool_id }
            })
        },
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
        },
        getHealthChecks() {
            return axios({
                url: `${baseURL}/health/get_health_checks`
            })
        },
    },
    mrktbackup: {
        inited() {
            return axios({
                url: `/backup/actors/threebot_deployer/repos_exist`
            })
        },
        snapshots() {
            return axios({
                url: `/backup/actors/threebot_deployer/snapshots`
            })
        },
        init(password) {
            return axios({
                url: `/backup/actors/threebot_deployer/init`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { password: password }
            })
        },
        backup(tags) {
            return axios({
                url: `/backup/actors/threebot_deployer/backup`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { tags: tags }
            })
        },
        enable: () => {
            return axios({
                url: `/backup/actors/threebot_deployer/enable_auto_backup`
            })
        },
        disable() {
            return axios({
                url: `/backup/actors/threebot_deployer/disable_auto_backup`
            })
        },
        enabled() {
            return axios({
                url: `/backup/actors/threebot_deployer/check_auto_backup`
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
    },
    license: {
        accept: () => {
            return axios({
                url: `/admin/api/accept/`,
                method: "get"
            })
        },
    }
}
