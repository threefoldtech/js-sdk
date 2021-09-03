<template>
  <div>
    <base-component
      title="Solutions Menu"
      icon="mdi-menu-left"
      url="/solutions"
    >
      <template #default>
        <v-card class="pa-3 ml-3">
          <v-card-title class="headline">
            <v-avatar size="50px" class="mr-5" tile>
              <v-img v-if="solution.image" :src="solution.image"></v-img>
              <v-icon v-else color="primary"
                >{{ solution.icon }} mdi-48px</v-icon
              >
            </v-avatar>
            <span>{{ solution.name }}</span>
            <v-tooltip top>
              <template v-slot:activator="{ on, attrs }">
                <a
                  class="chatflowInfo"
                  :href="solution.helpLink"
                  target="blank"
                >
                  <v-icon color="primary" large v-bind="attrs" v-on="on" right
                    >mdi-information-outline</v-icon
                  >
                </a>
              </template>
              <span>Go to Wiki</span>
            </v-tooltip>
          </v-card-title>

          <v-card-text>
            <span>{{ solution.description }}</span>
            <br />
            <br />
            <v-btn color="primary" @click.stop="restart(solution.type)"
              >New</v-btn
            >
            <v-btn
              color="primary"
              v-if="started(solution.type)"
              @click.stop="open(solution.type)"
              >Continue</v-btn
            >

            <v-divider class="my-5"></v-divider>
            <v-data-table
              :loading="loading"
              :headers="headers"
              :items="deployedSolutions"
              class="elevation-1"
            >
              <template slot="no-data">
                <p>No {{ solution.name.toLowerCase() }} workloads available</p>
              </template>
              <template v-slot:item.actions="{ item }">
                <v-tooltip top>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn icon @click.stop="showInfo(item)">
                      <v-icon v-bind="attrs" v-on="on" color="#206a5d"
                        >mdi-information-outline</v-icon
                      >
                    </v-btn>
                  </template>
                  <span>Show Information</span>
                </v-tooltip>
                <v-tooltip v-if="type == 'network'" top>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn icon @click.stop="addAccess(item)">
                      <v-icon v-bind="attrs" v-on="on" color="#206a5d"
                        >mdi-plus-network</v-icon
                      >
                    </v-btn>
                  </template>
                  <span>Add Access</span>
                </v-tooltip>
                <v-tooltip v-if="type == 'kubernetes'" top>
                  <template v-slot:activator="{ on, attrs }">
                    <a @click.stop="goNodesPage(item.Name)">
                      <v-icon v-bind="attrs" v-on="on" color="primary"
                        >mdi-Kubernetes</v-icon
                      >
                    </a>
                  </template>
                  <span>Nodes</span>
                </v-tooltip>
                <v-tooltip top>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn icon @click.stop="deleteSolution(item.wids)">
                      <v-icon v-bind="attrs" v-on="on" color="#810000"
                        >mdi-delete</v-icon
                      >
                    </v-btn>
                  </template>
                  <span>Delete</span>
                </v-tooltip>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </template>
    </base-component>
    <solution-info
      v-if="selected"
      v-model="dialogs.info"
      :data="selected"
    ></solution-info>
    <cancel-solution
      v-model="dialogs.cancelSolution"
      :wids="solutionWids"
    ></cancel-solution>
  </div>
</template>

<script>
module.exports = {
  props: { type: String },
  components: {
    "solution-info": httpVueLoader("./Info.vue"),
    "cancel-solution": httpVueLoader("./CancelSolution.vue"),
  },
  data() {
    return {
      loading: true,
      selected: null,
      solutionWids: null,
      dialogs: {
        info: false,
        cancelSolution: false,
      },
      headers: [
        { text: "Name", value: "Name" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      deployedSolutions: [],
      solutions: [...Object.values(SOLUTIONS)],
    };
  },
  computed: {
    solution() {
      return this.solutions.find((obj) => {
        return obj.type === this.type;
      });
    },
  },
  methods: {
    open(solutionType) {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: solutionType },
      });
    },
    restart(solutionType) {
      localStorage.removeItem(solutionType);
      this.open(solutionType);
    },
    started(solutionType) {
      return localStorage.hasOwnProperty(solutionType);
    },
    showInfo(data) {
      this.selected = data;
      this.dialogs.info = true;
    },
    addAccess(data) {
      let queryparams = { name: data.Name };
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: "network_access", queryparams: queryparams },
      });
    },
    getDeployedSolutions(solutionType) {
      this.$api.solutions
        .getDeployed(solutionType)
        .then((response) => {
          this.deployedSolutions = JSON.parse(response.data).data;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    goNodesPage(k8sName) {
      console.log("k8sName", k8sName);
      this.$router.push({
        name: "KubernetesNodes",
        params: { k8sName: k8sName },
      });
    },
    deleteSolution(wids) {
      this.solutionWids = wids;
      this.dialogs.cancelSolution = true;
    },
  },
  mounted() {
    this.getDeployedSolutions(this.type);
  },
};
</script>

<style scoped>
a.chatflowInfo {
  text-decoration: none;
  position: absolute;
  right: 10px;
  top: 10px;
}
</style>
