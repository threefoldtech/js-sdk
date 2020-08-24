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
          </v-card-title>

          <v-card-text>
            <span>{{solution.description}}</span>
            <br />
            <br />
            <v-btn color="primary" @click.stop="restart(solution.topic)">New</v-btn>
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
              v-for="(s, i) in deployedSolutions"
              :key="i"
              @click="showInfo(s)"
              outlined
            >{{ s.Name }}</v-chip>
          </v-card-text>
        </v-card>
      </template>
    </base-component>
    <solution-info v-if="selected" v-model="dialog" :data="selected" :type="selected"></solution-info>
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
      dialog: false,
      deployedSolutions: {},
      solutions: [...Object.values(APPS), ...Object.values(SOLUTIONS)]
    };
  },
  computed: {
    solution() {
      return this.solutions.find(obj => {
        return obj.type === this.type;
      });
    }
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
      this.dialog = true;
    },
    getDeployedSolutions(solution_type) {
      this.$api.solutions.getDeployed(solution_type).then(response => {
        this.deployedSolutions = JSON.parse(response.data).data;
      });
    }
  },
  mounted() {
    this.getDeployedSolutions(this.type);
  }
};
</script>
