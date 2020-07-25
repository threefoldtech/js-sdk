<template>
  <v-app>
    <v-app-bar app>
      <v-spacer></v-spacer>
      <v-menu v-if="user.username" v-model="menu" :close-on-content-click="false" offset-x>
        <template v-slot:activator="{ on }">
          <v-btn text v-on="on">
            <v-icon color="primary" left>mdi-account</v-icon> {{user.username}}
          </v-btn>
        </template>
        <v-card>
          <v-list>
            <v-list-item>
              <v-list-item-avatar>
                <v-avatar color="primary">
                  <v-icon dark>mdi-account-circle</v-icon>
                </v-avatar>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title>{{user.username}}</v-list-item-title>
                <v-list-item-subtitle>{{user.email}}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>

          <v-divider></v-divider>

          <v-card-actions>
            <v-btn block text href="/auth/logout">
              <v-icon color="primary" class="mr-2" left>mdi-exit-to-app</v-icon>Logout
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-menu>
    </v-app-bar>

    <v-navigation-drawer
      color="primary"
      class="elevation-3"
      :mini-variant="mini"
      app
      permanent
      dark
    >
      <v-sheet color="#148F77">
        <v-list class="text-center">
          <img src="./assets/3bot.png" :width="mini ? 40 : 128"/><br>
          <v-list-item v-if="identity">
            <v-list-item-content>
              <v-list-item-title>{{identity.name}} ({{identity.id}})</v-list-item-title>
              <v-list-item-subtitle>{{identity.email}}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-list-item v-else>
            <v-btn text block @click.stop="dialogs.identity = true">
              <v-icon left>mdi-account-cog</v-icon> Set identity
            </v-btn>
          </v-list-item>
        </v-list>
      </v-sheet>

      <div style="background-color: #ABB2B9; width:100%; height:5px"></div>

      <v-list class="mt-0 pt-0">
        <v-list-item v-for="page in pages" :key="page.name" :to="page.path" link>
          <v-list-item-icon>
            <v-icon>{{ page.meta.icon }}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title>{{ page.name }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="text-center pa-2">
          <v-btn icon @click.stop="mini = !mini">
            <v-icon>{{mini ? 'mdi-chevron-right' : 'mdi-chevron-left'}}</v-icon>
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-main>
      <router-view></router-view>
      <identities v-model="dialogs.identity"></identities>
      <popup></popup>
    </v-main>
  </v-app>
</template>

<script>
module.exports =  {
  data () { 
    return {
      user: {},
      identity: null,
      menu: false,
      mini:false,
      dialogs: {
        identity: false
      }
    } 
  },
  components: {
    identities: httpVueLoader("./Identity.vue")
  },
  computed: {},
  methods: {},
  computed: {
    pages () {
      return this.$router.options.routes.filter((page) => {
        return page.meta.listed
      })
    }
  },
  methods: {
    getCurrentUser () {
      this.$api.user.currentUser().then((response) => {
        this.user = response.data
      })
    },
    getIdentity () {
      this.$api.identity.get().then((response) => {
        this.identity = JSON.parse(response.data)
      })
    },
  },
  mounted() {
    this.getIdentity();
    this.getCurrentUser();
  }
};
</script>
