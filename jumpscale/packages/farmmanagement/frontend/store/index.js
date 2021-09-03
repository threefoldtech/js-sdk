import Vuex from '/weblibs/vuex/vuex.esm.browser.js'
import Vue from '/weblibs/vue/vue.js'

import farmmanagement from './farmmanagement.js'

Vue.use(Vuex)

export default new Vuex.Store({
    modules: {
        farmmanagement,
    }
})