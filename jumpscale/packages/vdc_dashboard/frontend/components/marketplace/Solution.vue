<template>
  <div>
    <base-component title="Apps Menu" icon="mdi-menu-left" url="/marketplacevdc" :loading="loading">
      <template #default>
        <v-card class="pa-3 ml-3">
          <v-card-title class="headline">
            <v-avatar v-if="solution.image" size="50px" class="mr-5" tile>
              <v-img :src="solution.image"></v-img>
            </v-avatar>
            <span>{{solution.name}}</span>
            <v-tooltip top>
              <template v-if="solution.helpLink" v-slot:activator="{ on, attrs }">
                <a
                  v-if="type!='all'"
                  class="chatflowInfo"
                  :href="solution.helpLink"
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
          <v-card-text v-if="type!='all'">
            <span>{{solution.description}}</span>
            <br />
            <br />
            <v-btn color="primary" @click.stop="restart(solution.type)">New</v-btn>
            <v-btn
              color="primary"
              v-if="started(solution.type)"
              @click.stop="open(solution.type)"
            >Continue</v-btn>
          </v-card-text>

          <v-card-text>
            <v-divider class="my-5"></v-divider>

            <v-data-table
              :loading="loading"
              :headers="headers"
              :items="deployedSolutions"
              class="elevation-1"
            >
              <template slot="no-data">No {{solution.name.toLowerCase()}} instances available</p></template>

              <template v-slot:item.domain="{ item }">
                <a v-if="item.domain !== ''" :href="`https://${item.Domain}/`">{{item.Domain}}</a>
                <p v-else> - </p>
              </template>
              <template v-slot:item.creation="{ item }">
                <div>{{ new Date(item.creation * 1000).toLocaleString('en-GB') }}</div>
              </template>
              <template v-slot:item.actions="{ item }">
                <v-tooltip top>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn v-if="item.Domain" icon :href="`https://${item.Domain}/`" target="_blank">
                      <v-icon v-bind="attrs" v-on="on" color="primary">mdi-web</v-icon>
                    </v-btn>
                  </template>
                  <span>Open in browser</span>
                </v-tooltip>
                <v-tooltip top>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn icon @click.stop="deleteSolution(item)">
                      <v-icon v-bind="attrs" v-on="on" color="#810000">mdi-delete</v-icon>
                    </v-btn>
                  </template>
                  <span>Delete</span>
                </v-tooltip>
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
    <cancel-solution v-if="selected" v-model="dialogs.cancelSolution" :namespace="selected.Namespace" :releasename="selected.Release" :solutionid="selected['User Supplied Values'].solution_uuid" :vdcname="selected['VDC Name']"></cancel-solution>
  </div>
</template>

<script>
module.exports = {
  props: {
    type: String,
  },

  components: {
    "solution-info": httpVueLoader("../base/Info.vue"),
    "cancel-solution": httpVueLoader("./Delete.vue"),
  },
  data() {
    return {
      loading: true,
      selected: null,
      dialogs: {
        info: false,
        cancelSolution: false,
      },
      headers: [
        { text: "Release", value: "Release" },
        { text: "URL", value: "domain" },
        { text: "Version", value: "Version" },
        { text: "Namespace", value: "Namespace" },
        { text: "Status", value: "Status" },
        { text: "Creation Time", value: "Creation" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      deployedSolutions: [],
      sections: SECTIONS,
    };
  },
  computed: {
    solution() {
      if(this.type==='all'){
        return {name: "Deployed Solutions",type: "all"}
      }
      for (section in this.sections) {
        if (Object.keys(this.sections[section].apps).includes(this.type)) {
          return this.sections[section].apps[this.type];
        }
      }
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
    deleteSolution(data) {
      this.selected = data;
      this.dialogs.cancelSolution = true;
    },
    getDeployedSolutions(solution_type) {
      if(solution_type === "all"){
        let solutionTypes = []
        for(sol in this.sections["All Solutions"].apps){
          solutionTypes.push(sol)
        }
        this.$api.solutions
        .getAllSolutions(solutionTypes)
        .then((response) => {
          this.deployedSolutions = response.data.data;
          chartTypeHeader = { text: "Solution Type", value: "Chart"}
          this.headers = [this.headers[0],chartTypeHeader,...this.headers.slice(1)]
        })
        .finally(() => {
          this.loading = false;
        });

      }
      else{
        this.$api.solutions
          .getSolutions(solution_type)
          .then((response) => {
            this.deployedSolutions = response.data.data;
          })
          .finally(() => {
            this.loading = false;
          });
      }
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
