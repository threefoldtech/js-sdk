<template>
  <div>
    <div style="padding: 40px; padding-top:20px">
      <template>
        <v-row>
          <v-spacer></v-spacer>
          <v-col>
            <v-autocomplete
              width="10"
              v-model="searchText"
              :items="[...apps, ...solutions]"
              :loading="loading"
              color="grey"
              hide-no-data
              hide-selected
              item-text="name"
              placeholder="Search for solutions"
              append-icon="mdi-magnify"
            ></v-autocomplete>
          </v-col>
          <v-spacer></v-spacer>
        </v-row>
        <h2 class="font-weight-black">Apps</h2>
        <v-row class="mt-2" align="start" justify="start">
          <v-card
            v-for="app in filteredApps"
            :key="app.topic"
            class="ma-2"
            width="280"
            :loading="loading"
            :disabled="loading"
          >
            <v-img v-if="app.image" class="mt-6" height="100px" :contain="true" :src="app.image"></v-img>
            <v-icon v-else class="ma-4" x-large color="primary">{{app.icon}}</v-icon>
            <v-card-title class="mx-2 font-weight-bold">
              {{app.name}}
              <v-chip
                v-if="solutionCount[app.type] !== undefined"
                :loading="true"
                class="ml-2"
                small
                outlined
              >{{solutionCount[app.type]}}</v-chip>
            </v-card-title>
            <v-card-text style="height:100px" class="mx-2 text--primary">
              {{app.description.length > SOLUTION_DESCRIPTION_MAXLENGTH ?
              app.description.slice(0, SOLUTION_DESCRIPTION_MAXLENGTH) + "..." :
              app.description}}
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn text medium @click.stop="openChatflow(app.type)">New</v-btn>
              <v-btn text medium @click.stop="viewWorkloads(app.type)">My workloads</v-btn>
            </v-card-actions>
          </v-card>
        </v-row>
        <br />

        <h2 class="font-weight-black mt-4">Advanced Solutions</h2>
        <v-row class="mt-2" align="start" justify="start">
          <v-card
            v-for="solution in filteredSolutions"
            :key="solution.type"
            class="ma-2"
            width="280"
            :loading="loading"
            :disabled="loading"
          >
            <v-img
              v-if="solution.image"
              class="mt-6"
              height="100px"
              :contain="true"
              :src="solution.image"
            ></v-img>
            <v-icon v-else class="ma-4" x-large color="primary">{{solution.icon}}</v-icon>
            <v-card-title class="mx-2 font-weight-bold">
              {{solution.name}}
              <v-chip
                v-if="solutionCount[solution.type] !== undefined"
                :loading="true"
                class="ml-2"
                small
                outlined
              >{{solutionCount[solution.type]}}</v-chip>
            </v-card-title>
            <v-card-text style="height:100px" class="mx-2 text--primary">
              {{solution.description.length > SOLUTION_DESCRIPTION_MAXLENGTH ?
              solution.description.slice(0, SOLUTION_DESCRIPTION_MAXLENGTH) + " ..." :
              solution.description}}
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn text medium @click.stop="openChatflow(solution.type)">New</v-btn>
              <v-btn text medium @click.stop="viewWorkloads(solution.type)">My workloads</v-btn>
            </v-card-actions>
          </v-card>
        </v-row>
      </template>
    </div>
  </div>
</template>

<script>
module.exports = {
  data() {
    return {
      SOLUTION_DESCRIPTION_MAXLENGTH: 130,
      loading: false,
      solutionCount: {},
      searchText: "",
      apps: Object.values(APPS),
      solutions: Object.values(SOLUTIONS)
    };
  },
  computed: {
    filteredSolutions() {
      if (this.searchText) {
        return this.solutions.filter(obj => {
          return obj.name === this.searchText;
        });
      } else return this.solutions;
    },
    filteredApps() {
      if (this.searchText) {
        return this.apps.filter(obj => {
          return obj.name === this.searchText;
        });
      } else return this.apps;
    }
  },
  methods: {
    openChatflow(solutionTopic) {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: solutionTopic }
      });
    },
    viewWorkloads(solutionType) {
      this.$router.push({ name: "Solution", params: { type: solutionType } });
    },
    getSolutionCount() {
      this.$api.solutions.getCount().then(response => {
        this.solutionCount = response.data.data;
      });
    }
  },
  mounted() {
    this.getSolutionCount();
  }
};
</script>
