<template>
  <div>
    <base-component :loading="loading">
      <template #actions>
        <v-btn color="primary" text @click.stop="restart(solution.type)">
          <v-icon left>mdi-package-variant-closed</v-icon> New 3bot
        </v-btn>

      </template>
      <template #default>
        <v-card class="pa-3 ml-3">
          <v-card-title class="headline">
            <v-avatar size="50px" class="mr-5" tile>
              <v-img v-if="solution.image" :src="solution.image"></v-img>
              <v-icon v-else color="primary">{{solution.icon}} mdi-48px</v-icon>
            </v-avatar>
            <span>{{solution.name}}</span>
          </v-card-title>

          <v-card-text style="font-size:1.1em">
            <span>{{solution.description}}</span>
            <br />
            <br />
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
    "solution-info": httpVueLoader("./Info.vue")
  },
  data() {
    return {
      loading: false,
      selected: null,
      dialogs: {
        info: false
      },
      deployedSolutions: {},
      solution: APPS["threebot"]
    };
  },
  methods: {
    open(solutionId) {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: solutionId }
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
    getDeployedSolutions() {
      this.$api.solutions.getDeployed().then(response => {
        this.deployedSolutions = response.data.data;
      });
    }
  },
  mounted() {
    this.getDeployedSolutions();
  }
};
</script>
