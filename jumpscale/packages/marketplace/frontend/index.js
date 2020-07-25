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
const home = httpVueLoader('./components/Home.vue')
const solutions = httpVueLoader('./components/solutions/Solutions.vue')
const solution = httpVueLoader('./components/solutions/Solution.vue')
const license = httpVueLoader('./components/License.vue')


Vue.component("base-component", baseComponent)
Vue.component("base-section", baseSection)
Vue.component("base-dialog", baseDialog)
Vue.component("external", external)
Vue.component("popup", popup)
Vue.component("code-area", code)

const router = new VueRouter({
  routes: [
    { name: "Home", path: '/', component: home, meta: { icon: "mdi-tune" } },
    { name: "License", path: '/license', component: license, meta: { icon: "mdi-apps" } },
    { name: "Solutions", path: '/:topic', component: solutions, props: true, meta: { icon: "mdi-apps" } },
    { name: "Solution", path: '/solutions/:topic', component: solution, props: true, meta: { icon: "mdi-tune" } },

  ]
})

router.beforeEach((to, from, next) => {
  const AllowedEndPoint = "api/allowed";
  axios.get(AllowedEndPoint).then(results => {
    let agreed = results.data.allowed;
    if (to.name !== "License" && !agreed) {
      next("/license");
    }
  })
  next();
})

Vue.use(VueCodemirror)

new Vue({
  el: '#app',
  components: { App: app },
  router,
  vuetify
})
