<template>
  <v-app>
    <v-app-bar app>
      <v-spacer></v-spacer>

      <v-menu v-model="menu" :close-on-content-click="false" offset-x>
        <template v-slot:activator="{ on }">
          <v-btn text v-on="on">
            <v-icon left>mdi-account</v-icon> {{user.username}}
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
              <v-icon color="primary" class="mr-2" left>mdi-exit-to-app</v-icon> Logout
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-menu>

    </v-app-bar>

    <v-main>
      <router-view></router-view>
      <popup></popup>
    </v-main>
  </v-app>
</template>

<script>
  module.exports =  {
    data () {
      return {
        user: {},
        menu: false,
      }
    },
    computed: {},
    methods: {},
    computed: {},
    methods: {
      getCurrentUser () {
        this.$api.admins.getCurrentUser().then((response) => {
          this.user = response.data
        })
      },
    },
    mounted () {
      this.getCurrentUser()
    }
  }
</script>
