<template>
  <div>
    <template>
      <div class="combox">
        <v-row>
          <h1 class="mx-auto text-center white--text">Decentralized Solutions on the ThreeFold Grid</h1>
          <v-col md="4" offset-md="4">
            <v-autocomplete
              auto-select-first

              solo
              v-model="selectedObject"
              :items="autoCompleteList"
              :loading="loading"
              color="grey"
              item-text="name"
              :item-value="(obj) => obj"
              label="Find a solution"
              append-icon="mdi-magnify"
              @change="viewWorkloads()"
            >
              <template v-slot:item="data">
                <template v-if="typeof data.item !== 'object'">
                  <v-list-item-content v-text="data.item"></v-list-item-content>
                </template>
                <template v-else>
                  <v-list-item-avatar>
                    <img :src="data.item.avatar" />
                  </v-list-item-avatar>
                  <v-list-item-content>
                    <v-list-item-title v-html="data.item.name"></v-list-item-title>
                  </v-list-item-content>
                </template>
              </template>
            </v-autocomplete>
          </v-col>
        </v-row>
      </div>

      <div class="categories">
        <v-row>
          <v-tabs vertical class="transparent-body">
            <v-toolbar-title class="mb-2 font-weight-bold">Categories</v-toolbar-title>
            <v-tab
              class="mr-5 justify-start"
              v-for="(section, key) in filteredSections"
              :key="key"
            >{{ key }} ({{ appsLength(key) }})</v-tab>
            <v-tab-item v-for="(section, key) in filteredSections" :key="key">
              <solutions-section
                :title="key"
                :apps="section.apps"
                :titletooltip="section.titleToolTip"
                :solutioncount="solutionCount"
                :loggedin="loggedin"
              ></solutions-section>
            </v-tab-item>
          </v-tabs>
        </v-row>
      </div>
      <br />
    </template>
  </div>
</template>

<script>
module.exports = {
  components: {
    "solutions-section": httpVueLoader("./base/SolutionsSection.vue"),
  },
  data() {
    return {
      loading: false,
      solutionCount: {},
      selectedObject: {},
      sections: SECTIONS,
      loggedin: this.$route.params.loggedin,
    };
  },
  computed: {
    filteredSections() {
      return Object.keys(this.sections)
        .filter((key) => Object.keys(this.sections[key].apps).length !== 0)
        .reduce((obj, key) => {
          obj[key] = this.sections[key];
          return obj;
        }, {});
    },
    autoCompleteList() {
      let ret = [];
      for (section in this.filteredSections) {
        if (section === "All Solutions") continue;
        const apps = Object.values(this.filteredSections[section].apps);
        ret.push({ header: section });
        for (let i = 0; i < apps.length; i++) {
          const app = apps[i];
          if (!app.disable)
            ret.push({
              name: app.name,
              group: section,
              avatar: app.image,
            });
        }
        ret.push({ divider: true });
      }
      return ret;
    },
  },
  methods: {
    viewWorkloads() {
      this.$router.push({
        name: "Solution",
        params: {
          type: this.selectedObject.name.toLowerCase(),
        },
      });
    },
    getSolutionCount() {
      this.$api.solutions.getCount().then((response) => {
        this.solutionCount = response.data.data;
      });
    },
    appsLength(app) {
      const apps = Object.values(this.filteredSections[app].apps);
      return apps.length;
    },
  },
  mounted() {
    this.getSolutionCount();
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
.combox {
  background-color: #1072ba;
  padding: 40px 20px 20px 20px;
}
.categories {
  padding: 50px;
}
.theme--light.v-tabs > .v-tabs-bar {
  background: transparent;
}
div.tabs [role="tab"] {
  justify-content: flex-start;
}
.v-toolbar__title {
  font-size: 1.5rem;
}
</style>
