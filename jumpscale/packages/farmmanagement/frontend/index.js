import Vue from '/weblibs/vue/vue.js'
import httpVueLoader from '/weblibs/http-vue-loader/httpVueLoader.js'
import Vuetify from '/weblibs/vuetify/vuetify.js'
import store from './store/index.js'
import router from './router/index.js'
import config from './config/index.js'
import './plugins/index.js'

document.addEventListener('DOMContentLoaded', (event) => {

    Vue.use(httpVueLoader)
    Vue.use(Vuetify)

    window.config = config


    new Vue({
        components: {
            app: httpVueLoader('./App/'),
        },
        vuetify: new Vuetify({
            icons: {
                iconfont: 'fa',
            },
            theme: {
                themes: {
                    light: {
                        primary: '#2d4052',
                        secondary: '#57be8e'
                    }
                }
            }
        }
        ),
        router,
        store,
        template: '<app></app>',
    }).$mount('#app')
})
