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
const markdownViewer = httpVueLoader('./components/MarkdownViewer.vue')

const baseComponent = httpVueLoader('./components/base/Component.vue')
const baseDialog = httpVueLoader('./components/base/Dialog.vue')
const baseSection = httpVueLoader('./components/base/Section.vue')
const external = httpVueLoader('./components/base/External.vue')
const popup = httpVueLoader('./components/base/Popup.vue')
const code = httpVueLoader('./components/base/Code.vue')
const vdc = httpVueLoader('./components/base/VDC.vue')
const s3 = httpVueLoader('./components/base/S3.vue')
const kubernetes = httpVueLoader('./components/base/Kubernetes.vue')
const ip = httpVueLoader('./components/base/IP.vue')

const app = httpVueLoader('./App.vue')
const home = httpVueLoader('./components/solutions/Solution.vue')
const solutionChatflow = httpVueLoader('./components/solutions/SolutionChatflow.vue')
const workloads = httpVueLoader('./components/solutions/Workloads.vue')
const license = httpVueLoader('./components/License.vue')
const terms = httpVueLoader('./components/Terms.vue')
const disclaimer = httpVueLoader('./components/Disclaimer.vue')

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
Vue.component("vdc", vdc)
Vue.component("s3", s3)
Vue.component("kubernetes", kubernetes)
Vue.component("ip", ip)

const router = new VueRouter({
    routes: [
        { name: "Home", path: '/', component: home, props: true, meta: { icon: "mdi-apps" } },
        { name: "License", path: '/license', component: license, meta: { icon: "mdi-apps" } },
        { name: "Terms", path: '/terms', component: terms, meta: { icon: "mdi-apps" } },
        { name: "Disclaimer", path: '/disclaimer', component: disclaimer, meta: { icon: "mdi-apps" } },
        { name: "SolutionChatflow", path: '/chats/:topic/:tname', component: solutionChatflow, props: true, meta: { icon: "mdi-tune" } },
        { name: "Workloads", path: '/workloads', component: workloads, meta: { icon: "mdi-tune" }, },
        {
            name: "VDC",
            path: '/workloads/:name',
            redirect: '/workloads/:name/s3',
            component: vdc,
            props: true,
            children: [{
                    name: 'S3',
                    path: 's3',
                    component: s3,
                    props: (route) => ({ query: route.query.vdc })
                },
                {
                    name: 'Kubernetes',
                    path: 'kubernetes',
                    component: kubernetes,
                    props: (route) => ({ query: route.query.vdc })
                }
            ]
        }
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