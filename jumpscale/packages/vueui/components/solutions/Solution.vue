<template>
  <div>
    <base-component title="Solutions Menu" icon="mdi-menu-left" url="/solutions">
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
                  :href="`https://manual.threefold.io/#/${solution.type}`"
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
              <span>Go to Wiki</span>
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
            <v-data-table
              :loading="loading"
              :headers="headers"
              :items="deployedSolutions"
              class="elevation-1"
            >
              <template slot="no-data">
                <p>No {{solution.name.toLowerCase()}} workloads available</p>
              </template>
              <template v-slot:item.actions="{ item }">
                <v-tooltip top>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn icon @click.stop="showInfo(item)">
                      <v-icon v-bind="attrs" v-on="on" color="#206a5d">mdi-information-outline</v-icon>
                    </v-btn>
                  </template>
                  <span>Show Information</span>
                </v-tooltip>
              </template>
            </v-data-table>
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
      loading: true,
      selected: null,
      dialogs: {
        info: false,
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
