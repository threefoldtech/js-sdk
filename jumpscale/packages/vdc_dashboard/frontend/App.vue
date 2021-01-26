<template>
  <v-app>
    <v-app-bar app>
      <router-link to="/" style="text-decoration: none">
        <v-row>
          <img
            class="ml-2"
            src="./assets/vdc_logo.png"
            height="30"
            max-width="266"
          />
        </v-row>
      </router-link>
      <v-spacer></v-spacer>

      <v-btn
        v-if="!['Marketplace', 'Solution'].includes(this.$route.name)"
        text
        href="#/marketplacevdc"
      >
        <v-icon color="primary" class="mr-2" right>mdi-apps</v-icon>Marketplace
      </v-btn>
      <v-btn v-else text href="#/settings">
        <v-icon color="primary" class="mr-2" right>mdi-server</v-icon>My VDC
      </v-btn>

      <v-menu v-model="menu" :close-on-content-click="false" offset-x>
        <template v-slot:activator="{ on }">
          <v-btn v-if="user" text v-on="on">
            <v-icon left>mdi-account</v-icon>
            {{ user.username }}
          </v-btn>
          <v-btn v-else text href="/auth/login?next_url=/vdc_dashboard/">
            <v-icon color="primary" class="mr-2" right>mdi-login-variant</v-icon
            >Login
          </v-btn>
        </template>
        <v-card v-if="user">
          <v-list>
            <v-list-item>
              <v-list-item-avatar>
                <v-avatar color="primary">
                  <v-icon dark>mdi-account-circle</v-icon>
                </v-avatar>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title>{{ user.username }}</v-list-item-title>
                <v-list-item-subtitle>{{ user.email }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-btn :loading="updateLoading" text color="blue" @click.stop="updateDashboard()"
                  >Update Dashboard</v-btn
                >
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-btn text color="blue" :to="'/terms'"
                  >Terms and Conditions</v-btn
                >
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-btn text color="blue" :to="'/disclaimer'">Disclaimer</v-btn>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-btn
                  text
                  :link="true"
                  color="blue"
                  href="https://manual.threefold.io/#/"
                  target="_blank"
                  >Manual</v-btn
                >
              </v-list-item-content>
            </v-list-item>
          </v-list>
          <v-divider></v-divider>
          <v-card-actions>
            <v-btn block text href="/auth/logout">
              <v-icon color="primary" class="mr-2" left>mdi-exit-to-app</v-icon
              >Logout
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
module.exports = {
  data() {
    return {
      user: {},
      menu: false,
      mini: false,
      updateLoading: false,
    };
  },
  methods: {
    getCurrentUser() {
      this.$api.admins
        .getCurrentUser()
        .then((response) => {
          this.user = response.data;
        })
        .catch(() => {
          this.user = null;
        });
    },
    updateDashboard() {
      this.updateLoading = true;
      this.$api.version
        .update()
        .then(() => {
          this.$router.go(0);
          this.updateLoading = false;
        })
    }
  },
  mounted() {
    this.getCurrentUser();
  },
};
</script>
