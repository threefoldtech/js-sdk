Vue.use(Vuex)
Vue.use(Vuetify)

Vue.prototype.$api = apiClient

const vuetify =  new Vuetify({
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

const app = httpVueLoader('./App.vue')
const solutions = httpVueLoader('./components/solutions/Solutions.vue')
const solution = httpVueLoader('./components/solutions/Solution.vue')

Vue.component("base-component", baseComponent)
Vue.component("base-section", baseSection)
Vue.component("base-dialog", baseDialog)
Vue.component("external", external)
Vue.component("popup", popup)

const router = new VueRouter({
  routes: [
    { name: "Solutions", path: '/', component: solutions, meta: {icon: "mdi-apps", listed: true } },
    { name: "Solution", path: '/solutions/:topic', component: solution, props: true, meta: {icon: "mdi-tune" } },
  ]
})

new Vue({
  el: '#app',
  components: { App: app },
  router,
  vuetify
})
