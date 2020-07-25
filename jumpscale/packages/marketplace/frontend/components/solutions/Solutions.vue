<template>
  <div>
    <base-component :loading="loading">
      <template #default>
        <v-card class="pa-3 ml-3">
          <v-card-title class="headline">
            <v-avatar size="50px" class="mr-5" tile>
              <v-img v-if="getSolutionData(topic).image" :src="getSolutionData(topic).image"></v-img>
              <v-icon v-else color="primary">{{getSolutionData(topic).icon}} mdi-48px</v-icon>
            </v-avatar>
            <span>{{getSolutionData(topic).name}}</span>
          </v-card-title>

          <v-card-text>
            <span>{{getSolutionData(topic).description}}</span>
            <br />
            <br />
            <v-btn color="primary" @click.stop="restart(topic)">New</v-btn>
            <v-btn color="primary" v-if="started(topic)" @click.stop="open(topic)">Continue</v-btn>

            <v-divider class="my-5"></v-divider>

            <v-chip
              class="ma-2"
              color="primary"
              min-width="100"
              v-for="(s, i) in deployedSolutions[topic]"
              :key="i"
              close
              @click="showInfo(s)"
              @click:close="showRemove(s)"
              outlined
            >{{ s.name }}</v-chip>
          </v-card-text>
        </v-card>
      </template>
    </base-component>

    <solution-info v-if="selected" v-model="dialogs.info" :data="selected"></solution-info>
    <solution-delete v-if="selected" v-model="dialogs.remove" :data="selected"></solution-delete>
  </div>
</template>

<script>
module.exports = {
  props: { topic: String },
  components: {
    "solution-info": httpVueLoader("./Info.vue"),
    "solution-delete": httpVueLoader("./Delete.vue")
  },
  watch: {
    topic: function() {
      this.getDeployedSolutions(this.topic);
    }
  },
  data() {
    return {
      loading: false,
      selected: null,
      dialogs: {
        info: false,
        remove: false
      },
      solutions: [
        {
          type: "ubuntu",
          name: "Ubuntu",
          image: "./assets/ubuntu.png",
          description:
            "A free and open-source Linux distribution based on Debian. Ubuntu is officially released in three editions: Desktop, Server, and Core(for internet of things devices and robots). This package is used to deploy an ubuntu container from an official flist on the grid using a chatflow."
        },
        {
          type: "kubernetes",
          name: "Kubernetes",
          image: "./assets/kubernetes.png",
          description:
            "Deploy a Kubernetes cluster with zdb using a chatflow. In this guide we will walk you through the provisioning of a full-blown kubernetes cluster on the TF grid. We will then see how to connect to it and interact using kubectl on our local machine. Finally we will go through some examples use cases to grasp the features offered by the cluster."
        },
        {
          type: "minio",
          name: "Minio",
          image: "./assets/minio.png",
          description:
            "MinIO is a high performance object storage. With the assist of the chatflow the user will deploy a machine with MinIO along with the number of zdbs needed for storage."
        },
        {
          type: "gitea",
          name: "Gitea",
          image: "./assets/gitea.png",
          description:
            "Gitea is a painless self-hosted Git service. It is similar to GitHub, Bitbucket, and GitLab."
        },
        {
          type: "network",
          name: "Network",
          icon: "mdi-network-outline",
          description:
            "Deploy a network on the grid and to connect your solutions together."
        },
        {
          type: "exposed",
          name: "Solution Expose",
          icon: "mdi-publish"
        },
        {
          type: "flist",
          name: "Generic Container",
          icon: "mdi-folder-multiple",
          description:
            "Spawn a container using specific flist provided by the user in the chatflow."
        },
        {
          type: "monitoring",
          name: "Monitoring",
          icon: "mdi-monitor-dashboard"
        },
        {
          type: "delegated_domain",
          name: "Domain Delegation",
          icon: "mdi-web"
        },
        {
          type: "4to6gw",
          name: "4 to 6 Gateway",
          icon: "mdi-router"
        },
        {
          type: "publisher",
          name: "Publisher",
          icon: "mdi-web-box",
          description:
            "Deploy a wiki, blog, website and access it via an IP and a public domain"
        },
        {
          type: "threebot",
          name: "Threebot",
          image: "./assets/3bot.png",
          description: "Deploy your Threebot on container."
        }
      ],
      deployedSolutions: {}
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
      this.dialogs.info = true;
    },
    showRemove(data) {
      this.selected = data;
      this.dialogs.remove = true;
    },
    getDeployedSolutions(solution_type) {
      this.$api.solutions.getDeployed(solution_type).then(response => {
        this.$set(this.deployedSolutions, solution_type, response.data.data);
      });
    },
    getSolutionData(topic) {
      return this.solutions.find(obj => {
        return obj.type === topic;
      });
    }
  },
  mounted() {
    this.getDeployedSolutions(this.topic);
  },
  updated() {}
};
</script>

<style scoped>
.v-tab {
  justify-content: left;
  text-align: left;
}
</style>
