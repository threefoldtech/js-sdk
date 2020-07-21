<template>
  <div>
    <base-component title="Solutions" icon="mdi-apps" :loading="loading">
      <template #default>
        <v-tabs class="text--left" background-color="transparent" vertical>
          <v-tab
            v-for="solution in solutions"
            :key="solution.topic"
            @click.stop="switchTo(solution.type)"
          >
            <v-avatar size="30px" class="mr-5">
              <v-img v-if="solution.image" :src="solution.image"></v-img>
              <v-icon v-else color="primary">{{solution.icon}}</v-icon>
            </v-avatar>
            {{solution.name}}
            <v-chip v-if="solutionCount[solution.type] !== undefined" :loading="true" class="ml-2" small outlined>{{solutionCount[solution.type]}}</v-chip>
          </v-tab>

          <v-tab-item v-for="solution in solutions" :key="solution.topic + '-content'">
            <v-card class="pa-3 ml-3">
              <v-card-title class="headline">
                <v-avatar size="50px" class="mr-5" tile>
                  <v-img v-if="solution.image" :src="solution.image"></v-img>
                  <v-icon v-else color="primary">{{solution.icon}} mdi-48px</v-icon>
                </v-avatar>
                <span>{{solution.name}}</span>
              </v-card-title>

              <v-card-text>
                <span>{{solution.description}}</span>
                <br />
                <br />
                <v-btn v-if="solution.topic !== 'all'" color="primary" @click.stop="restart(solution.topic)">New</v-btn>
                <v-btn
                  color="primary"
                  v-if="started(solution.topic)"
                  @click.stop="open(solution.topic)"
                >Continue</v-btn>

                <v-divider class="my-5"></v-divider>

                <v-chip
                  class="ma-2"
                  color="primary"
                  min-width="100"
                  v-for="(s, i) in deployedSolutions[solution.type]"
                  :key="i"
                  @click="showInfo(s)"
                  outlined
                >{{ solution.topic !== 'all' ? s.name : `${s.id} - ${s.status}` }}</v-chip>
              </v-card-text>
            </v-card>
          </v-tab-item>
        </v-tabs>
      </template>
    </base-component>

    <solution-info v-if="selected" v-model="dialog" :data="selected" :type="selected"></solution-info>
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
      solutions: Object.values(SOLUTIONS),
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
        this.solutionCount = JSON.parse(response.data).data;
      });
    },
    getDeployedSolutions(solution_type) {
      if (solution_type === "all_reservations") {
        this.$api.solutions.getAll().then(response => {
          this.$set(
            this.deployedSolutions,
            solution_type,
            JSON.parse(response.data).data
          );
        });
      } else
        this.$api.solutions.getDeployed(solution_type).then(response => {
          this.$set(
            this.deployedSolutions,
            solution_type,
            JSON.parse(response.data).data
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
