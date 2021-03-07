<template>
  <v-app>
    <v-app-bar app>
      <router-link to="/" style="text-decoration: none">
        <v-row>
          <img
            class="ml-2"
            src="./assets/TFNOW-Recovered.png"
            height="50"
            max-width="266"
          />
        </v-row>
      </router-link>
      <v-spacer></v-spacer>
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-chip
            v-bind="attrs"
            v-on="on"
            class="d-none d-md-inline ma-2 ml-4"
            color="#ea5455"
            label
            text-color="white"
          >
            <b>Demo on Testnet</b>
          </v-chip>
        </template>
        <pre>
This marketplace is a showcase of open source peer-to-peer apps built on top of the TF Grid.
We are in demo mode and running on testnet. Note your deployment will be cancelled automatically after three hours.
Forgive any instability you might encounter while our developers work out the kinks.
        </pre>
      </v-tooltip>
      <v-menu v-model="menu" :close-on-content-click="false" offset-x>
          <template v-slot:activator="{ on }">
            <v-btn v-if="user" text v-on="on">
              <v-icon left>mdi-account</v-icon>
              {{user.username}}
            </v-btn>
            <v-btn v-else text href="/auth/login?next_url=/marketplace/">
              <v-icon color="primary" class="mr-2" right>mdi-login-variant</v-icon>Login
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
                  <v-list-item-title>{{user.username}}</v-list-item-title>
                  <v-list-item-subtitle>{{user.email}}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-btn text color="blue" :to="'/terms'">Terms and Conditions</v-btn>
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
                  >Manual</v-btn>
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <v-divider></v-divider>
            <v-card-actions>
              <v-btn block text @click.stop="logout">
                <v-icon color="primary" class="mr-2" left>mdi-exit-to-app</v-icon>Logout
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
      solutionCount: {},
    };
  },
  methods: {
    getCurrentUser() {
      this.$api.admins.getCurrentUser().then((response) => {
        this.user = response.data;
      }).catch(() => {
        this.user = null;
      });
    },
    getSolutionCount() {
      this.$api.solutions.getCount().then((response) => {
        this.solutionCount = response.data.data;
      });
    },
    logout() {
      // clear cache on logout
      var backlen = history.length;
      history.go(-backlen);
      window.location.href = "/auth/logout";
    }
  },
  mounted() {
    this.getCurrentUser();
    this.getSolutionCount();
  },
};
</script>
