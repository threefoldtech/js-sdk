<template>
  <v-app>
    <v-app-bar app>
      <v-switch
        v-model="darkTheme"
        hide-details
        inset
        label="Dark mode"
      ></v-switch>
      <v-spacer></v-spacer>
      <v-menu offset-y>
        <template v-slot:activator="{ attrs, on }">
          <div v-if="notificationsCount">
            <v-badge
              color="red"
              offset-x="17"
              offset-y="12"
              class="mr-4"
              :content="notificationsCount"
            >
              <v-icon
                v-bind="attrs"
                v-on="on"
                color="primary"
                v-on:click="notificationsClick()"
                left
                >mdi-bell-ring</v-icon
              >
            </v-badge>
          </div>
          <div v-else>
            <v-icon
              class="pr-2"
              v-bind="attrs"
              v-on="on"
              color="primary"
              v-on:click="notificationsClick()"
              left
              >mdi-bell-outline</v-icon
            >
          </div>
        </template>

        <v-list class="notificationlist" v-if="notifications.length">
          <v-list-item
            v-for="item in notifications"
            :items="notifications"
            :key="item.id"
            link
          >
            <v-list-item-icon>
              <v-icon
                :color="notificationsIcons[item.level].color"
                class="ml-2"
                large
                >{{ notificationsIcons[item.level].icon }}</v-icon
              >
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title v-text="item.category"></v-list-item-title>
              <v-list-item-subtitle
                v-text="new Date(item.date * 1000).toLocaleString('en-GB')"
              ></v-list-item-subtitle>
              <v-list-item-title
                class="font-weight-bold"
                v-text="item.message"
              ></v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-menu>
      <v-chip label flat color="transparent" class="pr-5">
        <v-icon color="primary" left>mdi-clock-outline</v-icon>
        {{ timenow }}
      </v-chip>
      <v-menu
        v-if="user.username"
        v-model="menu"
        :close-on-content-click="false"
        offset-x
      >
        <template v-slot:activator="{ on }">
          <v-btn text v-on="on">
            <v-icon color="primary" left>mdi-account</v-icon>
            {{ user.username }}
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
                <v-list-item-title>{{ user.username }}</v-list-item-title>
                <v-list-item-subtitle>{{ user.email }}</v-list-item-subtitle>
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

    <v-navigation-drawer
      color="navbar"
      class="elevation-3"
      :mini-variant="mini"
      app
      permanent
      dark
    >
      <v-sheet color="logo">
        <v-list class="text-center">
          <img src="./assets/3bot.png" :width="mini ? 40 : 128" />
          <br />
          <v-list-item v-if="identity">
            <v-list-item-content>
              <v-list-item-title
                >{{ identity.name }} ({{ identity.id }})</v-list-item-title
              >
              <v-list-item-subtitle>
                <v-chip class="mt-2" outlined
                  >{{ identity.network }} Network</v-chip
                >
              </v-list-item-subtitle>
              <v-list-item-subtitle v-if="SDKVersion">
                <v-chip class="mt-2 px-6 py-6" outlined
                  >JS-NG: {{ NGVersion }}<br />JS-SDK: {{ SDKVersion }}</v-chip
                >
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
          <v-list-item v-else>
            <v-btn text block @click.stop="dialogs.identity = true">
              <v-icon left>mdi-account-cog</v-icon>Set identity
            </v-btn>
          </v-list-item>
        </v-list>
      </v-sheet>

      <v-list class="mt-0 pt-0">
        <v-list-item
          v-for="page in pages"
          :key="page.name"
          :to="page.path"
          link
        >
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
            <v-icon>{{
              mini ? "mdi-chevron-right" : "mdi-chevron-left"
            }}</v-icon>
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-main>
      <router-view
        @updatesidebarlist="isFarmManagementInstalled()"
      ></router-view>
      <identities v-model="dialogs.identity"></identities>
      <popup></popup>
    </v-main>

    <v-dialog v-model="announcement_dialog" persistent max-width="500">
      <v-card>
        <v-card-title class="headline"> Quick start guide </v-card-title>
        <v-card-text>
          We've created a wallet for you. Make sure your wallet is funded to
          extend your 3Bot before it expires.
          <br />
          Please visit the <a href="https://manual.threefold.io">manual</a> for
          more information.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="green darken-1" text @click="announced = true">
            Ok
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-footer app inset absolute>
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
  </v-app>
</template>

<script>
module.exports = {
  data() {
    return {
      darkTheme: this.$vuetify.theme.dark,
      user: {},
      identity: null,
      menu: false,
      mini: false,
      timenow: null,
      notifications: [],
      notificationsIcons: {
        info: {
          icon: "mdi-information-outline",
          color: "green",
        },
        warning: {
          icon: "mdi-alert-circle",
          color: "orange",
        },
        error: {
          icon: "mdi-close-circle-outline",
          color: "red",
        },
      },
      notificationsCount: null,
      notificationsListOpen: false,
      notificationInterval: null,
      NGVersion: null,
      SDKVersion: null,
      clockInterval: null,
      dialogs: {
        identity: false,
      },
      announced: true,
      pages: this.$router.options.routes.filter((page) => page.meta.listed),
    };
  },
  components: {
    identities: httpVueLoader("./Identity.vue"),
  },
  computed: {
    announcement_dialog() {
      return !this.announced;
    },
  },
  watch: {
    darkTheme(val) {
      $cookies.set("darkTheme", val ? "1" : "0");
      this.$vuetify.theme.dark = val;
    },
  },
  methods: {
    getCurrentUser() {
      this.$api.user.currentUser().then((response) => {
        this.user = response.data;
      });
    },
    getAnnouncementStatus() {
      this.$api.announcement.announced().then((response) => {
        console.log(response.data);
        this.announced = response.data["announced"];
        this.$api.announcement.announce();
      });
    },
    isFarmManagementInstalled() {
      this.$api.packages.getInstalled().then((response) => {
        let installed = JSON.parse(response.data).data.includes(
          "farmmanagement"
        );
        if (!installed) {
          this.pages = this.pages.filter(
            (item) => item.name != "Farm Management"
          );
        } else {
          this.pages = this.$router.options.routes.filter(
            (page) => page.meta.listed
          );
        }
      });
    },
    getIdentity() {
      this.$api.identity.get().then((response) => {
        this.identity = JSON.parse(response.data);
      });
    },
    getSDKVersion() {
      this.$api.admins.getSDKVersion().then((response) => {
        const versions = JSON.parse(response.data).data;
        this.NGVersion = versions["js-ng"];
        this.SDKVersion = versions["js-sdk"];
      });
    },
    setTimeLocal() {
      this.timenow = new Date().toLocaleString("en-GB");
    },
    getCookie(cname) {
      var name = cname + "=";
      var ca = document.cookie.split(";");
      for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == " ") {
          c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
          return c.substring(name.length, c.length);
        }
      }
      return "";
    },
    checkDarkMode() {
      let cookie = this.getCookie("darkTheme");
      if (cookie == "") this.$vuetify.theme.dark = this.darkTheme = false;
      else
        this.$vuetify.theme.dark = this.darkTheme =
          cookie == "1" ? true : false;
    },
    notificationsClick() {
      this.$api.admins.getNotifications().then((response) => {
        this.notifications = JSON.parse(response.data).data;
        this.notificationsCount = 0;
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
    this.checkDarkMode();
    this.getIdentity();
    this.getCurrentUser();
    this.getAnnouncementStatus();
    this.setTimeLocal();
    this.getSDKVersion();
    this.isFarmManagementInstalled();
    this.clockInterval = setInterval(() => {
      this.setTimeLocal();
    }, 1000);
    this.notificationInterval = setInterval(() => {
      this.$api.admins.getNotificationsCount().then((response) => {
        this.notificationsCount = JSON.parse(response.data).data;
      });
    }, 10000);
  },
  destroyed() {
    clearInterval(this.clockInterval);
    clearInterval(this.notificationInterval);
  },
};
</script>
<style>
.notificationlist {
  height: 400px;
  overflow-y: auto;
}
.v-footer {
  padding: 0;
}
</style>
