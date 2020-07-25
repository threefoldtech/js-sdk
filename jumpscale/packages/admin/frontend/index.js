Vue.use(Vuex)
Vue.use(Vuetify)

Vue.prototype.$api = apiClient

const vuetify = new Vuetify({
  icons: {
    iconfont: 'mdi'
  },
  theme: {
    themes: {
      light: {
        primary: '#1B4F72',
        secondary: '#CCCBCA',
        accent: '#59B88C',
        success: "#17A589",
        error: '#EC7063',
      },
    },
  }
})

const baseComponent = httpVueLoader('./components/base/Component.vue')
const baseDialog = httpVueLoader('./components/base/Dialog.vue')
const baseSection = httpVueLoader('./components/base/Section.vue')
const external = httpVueLoader('./components/base/External.vue')
const popup = httpVueLoader('./components/base/Popup.vue')
const code = httpVueLoader('./components/base/Code.vue')

const app = httpVueLoader('./App.vue')
const dashboard = httpVueLoader('./components/dashboard/Dashboard.vue')
const logs = httpVueLoader('./components/logs/Logs.vue')
const alerts = httpVueLoader('./components/alerts/Alerts.vue')
const wikis = httpVueLoader('./components/wikis/Wikis.vue')
const wiki = httpVueLoader('./components/wikis/Wiki.vue')
const solutions = httpVueLoader('./components/solutions/Solutions.vue')
const packages = httpVueLoader('./components/packages/Packages.vue')
const wallets = httpVueLoader('./components/wallets/Wallets.vue')
const capacity = httpVueLoader('./components/external/Capacity.vue')
const farmmanagement = httpVueLoader('./components/external/FarmManagement.vue')
const codeserver = httpVueLoader('./components/external/CodeServer.vue')
const notebooks = httpVueLoader('./components/external/Notebooks.vue')
const settings = httpVueLoader('./components/settings/Settings.vue')
const solution = httpVueLoader('./components/solutions/Solution.vue')
const backup = httpVueLoader('./components/backup/Backup.vue')


Vue.use(VueCodemirror)


Vue.mixin({
  methods: {
    alert(message, status) {
      this.$root.$emit('popup', message, status)
    }
  }
})

// Vue.component('code-mirror', )
Vue.component("base-component", baseComponent)
Vue.component("base-section", baseSection)
Vue.component("base-dialog", baseDialog)
Vue.component("external", external)
Vue.component("popup", popup)
Vue.component("code-area", code)

const router = new VueRouter({
  routes: [
    { name: "Dashboard", path: '/', component: dashboard, meta: { icon: "mdi-view-dashboard", listed: true } },
    { name: "Logs", path: '/logs', component: logs, meta: { icon: "mdi-text", listed: true } },
    { name: "Alerts", path: '/alerts', component: alerts, meta: { icon: "mdi-alert-outline", listed: true } },
    { name: "Wikis", path: '/wikis', component: wikis, meta: { icon: "mdi-book-open-outline", listed: true } },
    { name: "Wiki", path: '/wikis/:wiki', component: wiki, props: true, meta: { icon: "mdi-book-open" } },
    { name: "Packages", path: '/packages', component: packages, meta: { icon: "mdi-package-variant-closed", listed: true } },
    { name: "Wallets", path: '/wallets', component: wallets, meta: { icon: "mdi-wallet", listed: true } },
    { name: "Backup", path: '/backup', component: backup, meta: { icon: "mdi-database", listed: true } },
    { name: "Solutions", path: '/solutions', component: solutions, meta: { icon: "mdi-apps", listed: true } },
    { name: "Capacity", path: '/capacity', component: capacity, meta: { icon: "mdi-server", listed: true } },
    { name: "Farm Management", path: '/farmmanagement', component: farmmanagement, meta: { icon: "mdi-server", listed: true } },
    { name: "Codeserver", path: '/codeserver', component: codeserver, meta: { icon: "mdi-code-braces", listed: true } },
    { name: "Notebooks", path: '/notebooks', component: notebooks, meta: { icon: "mdi-language-python", listed: true } },
    { name: "Settings", path: '/settings', component: settings, meta: { icon: "mdi-tune", listed: true } },
    { name: "Solution", path: '/solutions/:topic', component: solution, props: true, meta: { icon: "mdi-tune" } },
  ]
})

new Vue({
  el: '#app',
  components: { App: app },
  router,
  vuetify
})
