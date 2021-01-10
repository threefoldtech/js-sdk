import VueRouter from '/weblibs/vue-router/vue-router.esm.browser.js'
import Vue from '/weblibs/vue/vue.js'
import httpVueLoader from '/weblibs/http-vue-loader/httpVueLoader.js'

Vue.use(VueRouter)

export default new VueRouter({
  routes: [
    {
      path: "/",
      component: httpVueLoader("./views/farmmanagement/"),
      name: 'home',
      meta: {
        icon: 'fa-home',
        position: 'top'
      }
    },
    {
      path: "/edit/:id",
      component: httpVueLoader("./views/farmedit/"),
      name: 'farmedit'
    },
  ]
})
