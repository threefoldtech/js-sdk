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
const markdownViewer = httpVueLoader('/vueui/base/MarkdownViewer.vue')

const baseComponent = httpVueLoader('/vueui/base/Component.vue')
const baseDialog = httpVueLoader('/vueui/base/Dialog.vue')
const baseSection = httpVueLoader('/vueui/base/Section.vue')
const external = httpVueLoader('/vueui/base/External.vue')
const popup = httpVueLoader('/vueui/base/Popup.vue')
const code = httpVueLoader('/vueui/base/Code.vue')

const app = httpVueLoader('./App.vue')
const home = httpVueLoader('./components/solutions/Solution.vue')
const solutionChatflow = httpVueLoader('./components/solutions/SolutionChatflow.vue')
const workloads = httpVueLoader('./components/solutions/Workloads.vue')
const license = httpVueLoader('./components/License.vue')
const terms = httpVueLoader('./components/Terms.vue')
const disclaimer = httpVueLoader('/vueui/Disclaimer.vue')

Vue.mixin({
    methods: {
        alert(message, status) {
            this.$root.$emit('popup', message, status)
        }
    }
})

Vue.component("base-component", baseComponent)
Vue.component("base-section", baseSection)
Vue.component("base-dialog", baseDialog)
Vue.component("external", external)
Vue.component("popup", popup)
Vue.component("code-area", code)
Vue.component("markdown-view", markdownViewer)

const router = new VueRouter({
    routes: [
        { name: "Home", path: '/', component: home, props: true, meta: { icon: "mdi-apps" } },
        { name: "License", path: '/license', component: license, meta: { icon: "mdi-apps" } },
        { name: "Terms", path: '/terms', component: terms, meta: { icon: "mdi-apps" } },
        { name: "Disclaimer", path: '/disclaimer', component: disclaimer, meta: { icon: "mdi-apps" } },
        { name: "SolutionChatflow", path: '/chats/:topic/:tname', component: solutionChatflow, props: true, meta: { icon: "mdi-tune" } },
        { name: "Workloads", path: '/workloads', component: workloads, meta: { icon: "mdi-tune" } },
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