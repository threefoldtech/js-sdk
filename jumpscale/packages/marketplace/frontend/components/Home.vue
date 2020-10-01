<template>
  <div>
    <div style="padding: 40px; padding-top: 20px">
      <template>
        <v-row>
          <v-spacer></v-spacer>
          <v-col>
            <v-autocomplete
              width="10"
              v-model="selectedObject"
              :items="autoCompleteList"
              :loading="loading"
              color="grey"
              item-text="name"
              :item-value="(obj) => obj"
              label="Search for solutions"
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
                    <v-list-item-title
                      v-html="data.item.name"
                    ></v-list-item-title>
                  </v-list-item-content>
                </template>
              </template>
            </v-autocomplete>
          </v-col>
          <v-spacer></v-spacer>
        </v-row>
        <solutions-section
          v-for="(section, key) in filteredSections"
          :key="key"
          :title="key"
          :apps="section.apps"
          :titletooltip="section.titleToolTip"
          :solutioncount="solutionCount"
        >
        </solutions-section>
        <br />
      </template>
    </div>
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
</style>
