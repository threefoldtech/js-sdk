<template>
  <div>
    <base-component title="Solutions" icon="mdi-apps" :loading="loading">
      <template #default>
        <v-card class="pa-3 ml-3">
          <v-card-title class="headline">
            <v-avatar size="50px" class="mr-5" tile>
              <v-img v-if="solution.image" :src="solution.image"></v-img>
              <v-icon v-else color="primary">{{solution.icon}} mdi-48px</v-icon>
            </v-avatar>
            <span>{{solution.name}}</span>
            <v-tooltip top>
              <template v-slot:activator="{ on, attrs }">
                <a
                  class="chatflowInfo"
                  :href="`https://manual-testnet.threefold.io/#/${solution.type}`"
                  target="blank"
                >
                  <v-icon
                    color="primary"
                    large
                    v-bind="attrs"
                    v-on="on"
                    right
                  >mdi-information-outline</v-icon>
                </a>
              </template>
              <span>Go to How-to Manual</span>
            </v-tooltip>
          </v-card-title>

          <v-card-text>
            <span>{{solution.description}}</span>
            <br />
            <br />
            <v-btn color="primary" @click.stop="restart(solution.type)">New</v-btn>
            <v-btn
              color="primary"
              v-if="started(solution.type)"
              @click.stop="open(solution.type)"
            >Continue</v-btn>

            <v-divider class="my-5"></v-divider>

            <v-chip
              class="ma-2"
              color="primary"
              min-width="100"
              v-for="(s, i) in deployedSolutions"
              :key="i"
              @click="showInfo(s)"
              outlined
            >{{ s["Pool id"] === undefined ? s.Name : s["Pool id"] }}</v-chip>
          </v-card-text>
        </v-card>
      </template>
    </base-component>
    <solution-info v-if="selected" v-model="dialogs.info" :data="selected"></solution-info>
  </div>
</template>

<script>
module.exports = {
  props: { type: String },
  components: {
    "solution-info": httpVueLoader("./Info.vue"),
  },
  data() {
    return {
      loading: false,
      selected: null,
      dialogs: {
        info: false,
      },
      deployedSolutions: {},
      solutions: [...Object.values(APPS)],
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
    open(solutionId) {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: solutionId },
      });
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
    getDeployedSolutions(solution_type) {
      this.$api.solutions.getDeployed(solution_type).then((response) => {
        if (solution_type === "pools") {
          const data = response.data.data;
          let parsedData = [];
          for (i in data) {
            let obj = {
              "Pool ID": data[i].pool_id,
              "Customer ID": data[i].customer_tid,
              "Available Cloud Units": data[i].cus,
              "Available Storage Units": data[i].sus,
              "Active Cloud Units": data[i].active_cu,
              "Active Storage Units": data[i].active_su,
              "Last Updated": new Date(data[i].last_updated * 1000),
              "Empty at": isNaN(new Date(data[i].empty_at * 1000))
                ? "-"
                : new Date(data[i].empty_at * 1000),
              "Node IDs": data[i].node_ids,
              "Active Workload IDs": data[i].active_workload_ids,
            };
            parsedData.push(obj);
          }
          this.deployedSolutions = parsedData;
        } else this.deployedSolutions = response.data.data;
      });
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
