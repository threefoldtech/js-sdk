<template>
  <div>
    <base-component title="Solutions" icon="mdi-apps" :loading="loading">
      <template #default>
        <div v-if="hasMigrated">
          <v-row>
            <v-spacer></v-spacer>
            <v-col>
              <v-autocomplete
                width="10"
                v-model="searchText"
                :items="[...solutions]"
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

          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span v-bind="attrs" v-on="on" class="soTitle font-weight-black mt-4">Solutions</span>
            </template>
            <span>Threefold grid primitives</span>
          </v-tooltip>
          <v-row class="mt-2" align="start" justify="start">
            <v-card
              v-for="solution in filteredSolutions"
              :key="solution.type"
              class="ma-2"
              width="290"
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
                <v-tooltip top>
                  <template v-slot:activator="{ on, attrs }">
                    <a
                      class="chatflowInfo"
                      :href="solution.helpLink"
                      target="blank"
                    >
                      <v-icon color="primary" v-bind="attrs" v-on="on" right>mdi-information-outline</v-icon>
                    </a>
                  </template>
                  <span>Go to Wiki</span>
                </v-tooltip>
              </v-card-title>
              <v-card-text style="height:100px" class="mx-2 text--primary">
                {{solution.description.length > SOLUTION_DESCRIPTION_MAXLENGTH ?
                solution.description.slice(0, SOLUTION_DESCRIPTION_MAXLENGTH) + " ..." :
                solution.description}}
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn text medium @click.stop="openChatflow(solution.type)">New</v-btn>
                <v-btn text medium @click.stop="viewWorkloads(solution.type)">My Workloads</v-btn>
              </v-card-actions>
            </v-card>
          </v-row>
          <br />
        </div>

        <v-card v-else class="mx-auto" max-width="344">
          <v-card-text>
            <div>Have to migrate first</div>
            <p class="display-1 text--primary">migrate</p>
            <div class="text--primary">
              The explorer has been upgraded, so you need to initialize the migration of your old reservations to be able to use them.
              <br />To migrate please click on the bellow button.
            </div>
          </v-card-text>
          <v-card-actions>
            <v-btn text color="deep-purple accent-4" @click="migrate">migrate</v-btn>
          </v-card-actions>
        </v-card>
      </template>
    </base-component>
  </div>
</template>
<script>
module.exports = {
  data() {
    return {
      SOLUTION_DESCRIPTION_MAXLENGTH: 130,
      loading: false,
      hasMigrated: true,
      solutions: Object.values(SOLUTIONS),
      solutionCount: {},
      searchText: "",
    };
  },
  computed: {
    filteredSolutions() {
      if (this.searchText) {
        return this.solutions.filter((obj) => {
          return obj.name === this.searchText;
        });
      } else return this.solutions;
    },
  },
  methods: {
    openChatflow(solutionTopic) {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: solutionTopic },
      });
    },
    viewWorkloads(solutionType) {
      this.$router.push({ name: "Solution", params: { type: solutionType } });
    },
    getSolutionCount() {
      this.$api.solutions.getCount().then((response) => {
        this.solutionCount = JSON.parse(response.data).data;
      });
    },
    migrate() {
      this.$api.solutions.migrate().then((response) => {
        window.location.reload();
      });
    },
  },
  mounted() {
    this.getSolutionCount();
  },
  created() {
    this.$api.solutions.hasMigrated().then((response) => {
      this.hasMigrated = JSON.parse(response.data).result;
    });
  },
};
</script>

<style scoped>
span.soTitle {
  font-size: 27;
}
a.chatflowInfo {
  text-decoration: none;
  position: absolute;
  right: 10px;
}
</style>
