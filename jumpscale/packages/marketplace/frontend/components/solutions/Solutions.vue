<template>
  <div>
    <base-component title="Solutions" icon="mdi-apps" :loading="loading">
      <template #default>
        <v-tabs class="text--left" background-color="transparent" vertical>
          <v-tab
            v-for="solution in solutions"
            :key="solution.id"
            @click.stop="switchTo(solution.type)"
          >
            <v-avatar size="30px" class="mr-5">
              <v-img v-if="solution.image" :src="solution.image"></v-img>
              <v-icon v-else color="primary">{{solution.icon}}</v-icon>
            </v-avatar>
            {{solution.name}}
            <v-chip :loading="true" class="ml-2" small outlined>{{solutionCount[solution.type] || 0}}</v-chip>
          </v-tab>

          <v-tab-item v-for="solution in solutions" :key="solution.id + '-content'">
              <v-card class="pa-3 ml-3">
            <v-card-title class="headline">
              <v-avatar size="50px" class="mr-5" tile>
                <v-img v-if="solution.image" :src="solution.image"></v-img>
                <v-icon v-else color="primary">{{solution.icon}} mdi-48px</v-icon>
              </v-avatar>
              <span>{{solution.name}}</span>
            </v-card-title>

            <v-card-text>
              <span>{{solution.description}}</span><br><br>
              <v-btn color="primary" @click.stop="restart(solution.type)">New</v-btn>
              <v-btn color="primary" v-if="started(solution.type)" @click.stop="open(solution.type)">Continue</v-btn>

              <v-divider class="my-5"></v-divider>

              <v-chip class="ma-2" color="primary" min-width="100" v-for="(s, i) in deployedSolutions[solution.type]" :key="i" @click="showInfo(s)" outlined>
                {{ s.name }}
              </v-chip>

            </v-card-text>
          </v-tab-item>
        </v-tabs>
      </template>
    </base-component>

    <solution-info v-if="selected" v-model="dialog" :data="selected"></solution-info>
  </div>
</template>

<script>
module.exports = {
  components: {
    "solution-info": httpVueLoader("./Info.vue")
  },
  data() {
    return {
      loading: false,
      selected: null,
      dialog: false,
      solutions: [
        {
          id: "ubuntu_deploy",
          type: "ubuntu",
          name: "Ubuntu",
          image: "./assets/ubuntu.png",
          description:
            "A free and open-source Linux distribution based on Debian. Ubuntu is officially released in three editions: Desktop, Server, and Core(for internet of things devices and robots). This package is used to deploy an ubuntu container from an official flist on the grid using a chatflow."
        },
        {
          id: "kubernetes_deploy",
          type: "kubernetes",
          name: "Kubernetes",
          image: "./assets/kubernetes.png",
          description:
            "Deploy a Kubernetes cluster with zdb using a chatflow. In this guide we will walk you through the provisioning of a full-blown kubernetes cluster on the TF grid. We will then see how to connect to it and interact using kubectl on our local machine. Finally we will go through some examples use cases to grasp the features offered by the cluster."
        },
        {
          id: "minio_deploy",
          type: "minio",
          name: "Minio",
          image: "./assets/minio.png",
          description:
            "MinIO is a high performance object storage. With the assist of the chatflow the user will deploy a machine with MinIO along with the number of zdbs needed for storage."
        },
        {
          id: "gitea_deploy",
          type: "gitea",
          name: "Gitea",
          image: "./assets/gitea.png",
          description:
            "Gitea is a painless self-hosted Git service. It is similar to GitHub, Bitbucket, and GitLab."
        },
        {
          id: "network_deploy",
          type: "network",
          name: "Network",
          icon: "mdi-network-outline",
          description:
            "Deploy a network on the grid and to connect your solutions together."
        },
        {
          id: "solution_expose",
          type: "exposed",
          name: "Solution Expose",
          icon: "mdi-publish"
        },
        {
          id: "flist_deploy",
          type: "flist",
          name: "Generic Flist",
          icon: "mdi-folder-multiple",
          description:
            "Spawn a container using specific flist provided by the user in the chatflow."
        },
        {
          id: "monitoring_deploy",
          type: "monitoring",
          name: "Monitoring",
          icon: "mdi-monitor-dashboard"
        },
        {
          id: "domain_delegation",
          type: "delegated_domain",
          name: "Domain Delegation",
          icon: "mdi-web"
        },
        {
          id: "4to6gw",
          type: "4to6gw",
          name: "4 to 6 Gateway",
          icon: "mdi-router"
        }
      ],
      deployedSolutions: {},
      solutionCount: {}
    };
  },
  methods: {
    open(solutionId) {
      this.$router.push({ name: "Solution", params: { topic: solutionId } });
    },
    restart(solutionId) {
      localStorage.removeItem(solutionId);
      this.open(solutionId);
    },
    started(solution_type) {
      return localStorage.hasOwnProperty(solution_type);
    },
    showInfo(data) {
      this.selected = data;
      this.dialog = true;
    },
    switchTo(solution_type) {
      if (this.deployedSolutions[solution_type] == undefined) {
        this.getDeployedSolutions(solution_type);
      }
    },
    getSolutionCount() {
      this.$api.solutions.getCount().then(response => {
        this.solutionCount = response.data.data;
      });
    },
    getDeployedSolutions(solution_type) {
      this.$api.solutions.getDeployed(solution_type).then(response => {
        this.$set(
          this.deployedSolutions,
          solution_type,
          response.data.data
        );
      });
    }
  },
  mounted() {
    this.getSolutionCount();
  }
};
</script>

<style scoped>
.v-tab {
  justify-content: left;
  text-align: left;
}
</style>
