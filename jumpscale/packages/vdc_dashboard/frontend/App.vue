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
                <v-btn
                  :loading="updateLoading"
                  text
                  color="blue"
                  @click.stop="updateDashboard()"
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
            <v-btn block text @click.stop="logout">
              <v-icon color="primary" class="mr-2" left>mdi-exit-to-app</v-icon
              >Logout
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-menu>
    </v-app-bar>

    <v-main>
      <router-view @update-dashboard="updateDashboard"></router-view>
      <popup></popup>
    </v-main>
    <v-footer inset>
      <v-col class="text-left" cols="6">
        &copy; {{ new Date().getFullYear() }} JS-SDK
      </v-col>
      <v-col class="text-right" cols="6">
        <v-btn
          depressed
          color="primary"
          href="https://threefold.io/support"
          target="_blank"
          >Support</v-btn
        >
      </v-col>
    </v-footer>
    <v-dialog v-model="dialog" hide-overlay persistent width="300">
      <v-card :color="dialogColor" dark>
        <v-card-text class="pt-4">
          {{ dialogMessage }}
          <v-progress-linear
            v-if="dialogLinear"
            indeterminate
            color="white"
            class="mb-0"
          ></v-progress-linear>
        </v-card-text>
        <v-card-actions v-if="!dialogLinear">
          <v-spacer></v-spacer>
          <v-btn color="white darken-1" text @click="dialog = false">
            close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
      dialog: false,
      dialogLinear: true,
      dialogColor: "primary",
      dialogMessage: "Updating the VDC...",
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
    async serverIsrunningCheck() {
      let startTime = new Date();
      let timeNow = new Date();
      let timeSpent = 0;
      while (timeSpent <= 5) {
        await this.$api.server
          .isRunning()
          .then(() => {
            console.log("server started");
            // refresh the page
            location.reload(true);
          })
          .catch(() => {
            console.log("server is restarting...");
          });
        timeNow = new Date();
        timeSpent = (startTime.getTime() - timeNow.getTime()) / 1000;
        timeSpent /= 60; //convert to min
      }
      this.dialogColor = "error";
      this.dialogLinear = false;
      this.dialogMessage = "Error in updating the VDC, please contact support.";
    },
    async updateDashboard() {
      this.menu = false;
      // show massege say "request success and now the server is restarting"
      this.dialog = true;
      await this.$api.version
        .update()
        .then(() => {
          // wait until the server start
          setTimeout(async () => {
            await this.serverIsrunningCheck();
          }, 1000 * 5);
        })
        .catch((error) => {
          this.menu = false;
          this.dialogColor = "error";
          this.dialogLinear = false;
          this.dialogMessage =
            "Error in updating the VDC, please contact support.";
          console.log(`Can't update the vdc ${error}`);
        });
    },
    logout() {
      // clear cache on logout
      var backlen = history.length;
      history.go(-backlen);
      window.location.href = "/auth/logout";
    },
  },
  mounted() {
    this.getCurrentUser();
  },
};
</script>

<style scoped>
.v-footer {
  background-color: #fbfcfc !important;
}
</style>
