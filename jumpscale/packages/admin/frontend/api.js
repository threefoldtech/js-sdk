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
        listLogs: (appName) => {
            return axios({
                url: `${baseURL}/logs/list_logs`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { app_name: appName }
            })
        },
        delete: (appName) => {
            return axios({
                url: `${baseURL}/logs/remove_records`,
                method: "post",
                data: { app_name: appName }
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
        import: (name, secret) => {
            return axios({
                url: `${baseURL}/wallet/import_wallet`,
                method: "post",
                data: { name: name, secret: secret }
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
        },
        listChatEndpoints: (name) => {
            return axios({
                url: `${baseURL}/packages/list_chat_urls`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { name: name }
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
        getConfig: () => {
            return axios({
                url: `${baseURL}/admin/get_config`
            })
        },
        getSDKVersion: () => {
            return axios({
                url: `${baseURL}/admin/get_sdk_version`
            })
        },
        getDeveloperOptions: () => {
            return axios({
                url: `${baseURL}/admin/get_developer_options`
            })
        },
        setDeveloperOptions: (testCert, overProvision, escalationEmails, sortNodesBySRU) => {
            return axios({
                url: `${baseURL}/admin/set_developer_options`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { test_cert: testCert, over_provision: overProvision, sort_nodes_by_sru: sortNodesBySRU, escalation_emails: escalationEmails }
            })
        },
        clearBlockedNodes: () => {
            return axios({
                url: `${baseURL}/admin/clear_blocked_nodes`,
            })
        },
        getThreebotState: () => {
            return axios({
                url: `/admin/api/export`,
                headers: { 'Content-Type': 'application/json' },
                responseType: 'arraybuffer',
                method: "get"
            })
        },
        clearBlockedManagedDomains: () => {
            return axios({
                url: `${baseURL}/admin/clear_blocked_managed_domains`,
            })
        },
        getNotifications: () => {
            return axios({
                url: `${baseURL}/admin/get_notifications`,
            })
        },
        getNotificationsCount: () => {
            return axios({
                url: `${baseURL}/admin/get_notifications_count`,
            })
        }
    },
    emailServerConfig: {
        get: () => {
            return axios({
                url: `${baseURL}/admin/get_email_server_config`
            })
        },
        set: (host, port, username, password) => {
            return axios({
                url: `${baseURL}/admin/set_email_server_config`,
                method: "post",
                headers: { "Content-Type": "application/json" },
                data: {
                    host: host,
                    port: port,
                    username: username,
                    password: password
                }
            })
        },
    },
    escalationEmails: {
        list: () => {
            return axios({
                url: `${baseURL}/admin/list_escalation_emails`
            })
        },
        add: (email) => {
            return axios({
                url: `${baseURL}/admin/add_escalation_email`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { email: email }
            })
        },
        delete: (email) => {
            return axios({
                url: `${baseURL}/admin/delete_escalation_email`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { email: email }
            })
        }

    },
    identities: {
        list: () => {
            return axios({
                url: `${baseURL}/admin/list_identities`
            })
        },
        add: (display_name, tname, email, words, admins) => {
            return axios({
                url: `${baseURL}/admin/add_identity`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { display_name, tname, email, words, admins }
            })
        },
        generateMnemonic: () => {
            return axios({
                url: `${baseURL}/admin/generate_mnemonic`
            })
        },
        checkTNameExists: (tname) => {
            return axios({
                url: `${baseURL}/admin/check_tname_exists`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { tname: tname }
            })
        },
        checkInstanceName: (name) => {
            return axios({
                url: `${baseURL}/admin/check_identity_instance_name`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { name: name }
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
        currentIdentity: () => {
            return axios({
                url: `${baseURL}/admin/get_current_identity_name`
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
    sshkeys: {
        list: () => {
            return axios({
                url: `${baseURL}/admin/list_sshkeys`
            })
        },
        add: (id, sshkey) => {
            return axios({
                url: `${baseURL}/admin/add_sshkey`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { key_id: id, sshkey: sshkey }
            })
        },
        delete: (id) => {
            return axios({
                url: `${baseURL}/admin/delete_sshkey`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { key_id: id }
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
        set: (label, tname, email, words) => {
            return axios({
                url: `${baseURL}/identity/set_identity`,
                method: "post",
                headers: { 'Content-Type': 'application/json' },
                data: { label: label, tname: tname, email: email, words: words }
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
    },
    announcement: {
        announced: () => {
            return axios({
                url: `/admin/api/announced`,
                method: "get"
            })
        },
        announce: () => {
            return axios({
                url: `/admin/api/announce`,
                method: "get"
            })
        },
    }
}
