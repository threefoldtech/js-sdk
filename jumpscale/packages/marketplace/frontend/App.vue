<template>
  <v-app>
    <v-app-bar app>
      <v-spacer></v-spacer>

      <v-menu v-model="menu" :close-on-content-click="false" offset-x>
        <template v-slot:activator="{ on }">
          <v-btn text v-on="on">
            <v-icon left>mdi-account</v-icon>
            {{user.username}}
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
      v-if="sidebar"
      color="primary"
      class="elevation-3"
      :mini-variant="mini"
      app
      permanent
      dark
      :width="280"
    >
      <v-sheet color="#148F77">
        <v-list class="text-center">
          <img src="./assets/3bot.png" :width="mini ? 40 : 128" />
          <br />
        </v-list>
      </v-sheet>

      <div style="background-color: #ABB2B9; width:100%; height:5px"></div>

      <v-list class="mt-0 pt-0">
        <v-list-item v-for="page in pages" :key="page.name" :to="page.path" link>
          <v-list-item-icon>
            <v-img height="30px" width="30px" v-if="page.meta.img" :src="page.meta.img"></v-img>
            <v-icon v-else color="white">{{page.meta.icon}}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title>
              {{ page.name }}
              <v-chip :loading="true" class="ml-2" small outlined>{{solutionCount[page.type] || 0}}</v-chip>
            </v-list-item-title>
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
      sidebar: true
    };
  },
  computed: {},
  methods: {},
  computed: {
    pages() {
      return [
        {
          name: "Network",
          type: "network",
          path: "/network",
          meta: { icon: "mdi-network-outline" }
        },
        {
          name: "Ubuntu",
          type: "ubuntu",
          path: "/ubuntu",
          meta: { img: "./assets/ubuntu.png" }
        },
        {
          name: "Generic Container",
          type: "flist",
          path: "/flist",
          meta: { icon: "mdi-folder-multiple" }
        },
        {
          name: "Kubernetes",
          type: "kubernetes",
          path: "/kubernetes",
          meta: { img: "./assets/kubernetes.png" }
        },
        {
          name: "Minio",
          type: "minio",
          path: "/minio",
          meta: { img: "./assets/minio.png" }
        },
        {
          name: "Monitoring",
          type: "monitoring",
          path: "/monitoring",
          meta: { icon: "mdi-monitor-dashboard" }
        },
        {
          name: "Gitea",
          type: "gitea",
          path: "/gitea",
          meta: { img: "./assets/gitea.png" }
        },
        {
          name: "Solution Expose",
          type: "exposed",
          path: "/exposed",
          meta: { icon: "mdi-publish" }
        },
        {
          name: "Domain Delegation",
          type: "delegated_domain",
          path: "/delegated_domain",
          meta: { icon: "mdi-web" }
        },
        {
          name: "4 to 6 Gateway",
          type: "4to6gw",
          path: "/4to6gw",
          meta: { icon: "mdi-router" }
        },
        {
          name: "Publisher",
          type: "publisher",
          path: "/publisher",
          meta: { icon: "mdi-web-box" }
        },
        {
          type: "threebot",
          name: "Threebot",
          path: "/threebot",
          meta: { img: "./assets/3bot.png" }
        }
      ];
    }
  },
  methods: {
    getCurrentUser() {
      this.$api.admins.getCurrentUser().then(response => {
        this.user = response.data;
      });
    },
    getSolutionCount() {
      this.$api.solutions.getCount().then(response => {
        this.solutionCount = response.data.data;
      });
    }
  },
  mounted() {
    this.getCurrentUser();
    this.getSolutionCount();

    this.$root.$on("sidebar", sidebar => {
      this.sidebar = sidebar;
    });
  }
};
</script>
