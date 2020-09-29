<template>
  <div>
    <v-tooltip v-if="titletooltip" top>
      <template v-slot:activator="{ on, attrs }">
        <span v-bind="attrs" v-on="on" class="soTitle font-weight-black mt-4">{{
          title
        }}</span>
      </template>
      <span>{{ titletooltip }}</span>
    </v-tooltip>
    <span v-else class="soTitle font-weight-black mt-4">{{ title }}</span>
    <v-row class="mt-2" align="start" justify="start">
      <v-card
        v-for="app in filteredApps"
        :key="app.type"
        class="ma-2"
        width="320"
        :loading="loading"
        :disabled="loading"
      >
        <v-img
          class="mt-6"
          height="70px"
          :contain="true"
          :src="app.image"
        ></v-img>
        <v-card-title class="mx-2 font-weight-black">
          {{ app.name }}
          <v-chip
            v-if="
              solutioncount !== undefined &&
              solutioncount[app.type] !== undefined
            "
            class="ml-2"
            small
            outlined
            >{{ solutioncount[app.type] }}</v-chip
          >
          <v-tooltip top>
            <template v-slot:activator="{ on, attrs }">
              <a class="chatflowInfo" :href="app.helpLink" target="blank">
                <v-icon color="primary" v-bind="attrs" v-on="on" right
                  >mdi-information-outline</v-icon
                >
              </a>
            </template>
            <span>Go to How-to Manual</span>
          </v-tooltip>
        </v-card-title>
        <v-card-text style="height: 100px" class="mx-2 text--primary">
          {{
            app.description.length > SOLUTION_DESCRIPTION_MAXLENGTH
              ? app.description.slice(0, SOLUTION_DESCRIPTION_MAXLENGTH) + "..."
              : app.description
          }}
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text medium @click.stop="openChatflow(app.type)">New</v-btn>
          <v-btn text medium @click.stop="viewWorkloads(app)"
            >My Workloads</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-row>
    <v-divider class="my-4"></v-divider>
  </div>
</template>

<script>
module.exports = {
  props: {
    title: String,
    titletooltip: String,
    apps: Object,
    solutioncount: Object,
  },
  data() {
    return {
      SOLUTION_DESCRIPTION_MAXLENGTH: 100,
      loading: false,
      searchText: "",
    };
  },
  computed: {
    filteredApps() {
      return Object.values(this.apps).filter((app) => !app.disable);
    },
  },
  methods: {
    openChatflow(solutionTopic) {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: solutionTopic },
      });
    },
    viewWorkloads(solution) {
      this.$router.push({
        name: "Solution",
        params: { type: solution.type },
      });
    },
  },
};
</script>

<style scoped>
span.soTitle {
  font-size: 20;
}
a.chatflowInfo {
  text-decoration: none;
  position: absolute;
  right: 10px;
}
</style>
