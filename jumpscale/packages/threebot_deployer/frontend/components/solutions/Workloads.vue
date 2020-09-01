<template>
  <div>
    <base-component title="MY 3BOTS" icon="mdi-clipboard-list-outline" :loading="loading">
      <template #actions>
        <v-btn color="primary" text @click.stop="openChatflow()">
          <v-icon left>mdi-plus</v-icon>New
        </v-btn>
      </template>

      <template #default>
        <v-data-table
          :loading="loading"
          :headers="headers"
          :items="deployed3Bots"
          class="elevation-1"
        >
          <template v-slot:item.domain="{ item }">
            <a :href="`https://${item.Domain}/admin`">{{item.Domain}}</a>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-tooltip top>
              <template v-slot:activator="{ on, attrs }">
                <v-btn icon :href="`https://${item.Domain}/admin`">
                  <v-icon v-bind="attrs" v-on="on" color="primary">mdi-web</v-icon>
                </v-btn>
              </template>
              <span>Open in browser</span>
            </v-tooltip>
            <v-tooltip top>
              <template v-slot:activator="{ on, attrs }">
                <v-btn icon @click.stop="delete3Bot(item.wids)">
                  <v-icon v-bind="attrs" v-on="on" color="#810000">mdi-delete</v-icon>
                </v-btn>
              </template>
              <span>Delete</span>
            </v-tooltip>
            <v-tooltip top>
              <template v-slot:activator="{ on, attrs }">
                <v-btn icon @click.stop="open(item)">
                  <v-icon v-bind="attrs" v-on="on" color="#206a5d">mdi-information-outline</v-icon>
                </v-btn>
              </template>
              <span>Show Information</span>
            </v-tooltip>
          </template>
        </v-data-table>
      </template>
    </base-component>
    <solution-info v-if="selected" v-model="dialogs.info" :data="selected"></solution-info>
    <cancel-workload v-model="dialogs.cancelWorkload" :wids="wids"></cancel-workload>
  </div>
</template>

<script>
module.exports = {
  components: {
    "solution-info": httpVueLoader("./Info.vue"),
    "cancel-workload": httpVueLoader("./Delete.vue"),
  },
  data() {
    return {
      threebot_data: APPS["threebot"],
      dialogs: {
        info: false,
        cancelWorkload: false,
      },
      selected: null,
      loading: true,
      headers: [
        { text: "Name", value: "Name" },
        { text: "URL", value: "domain" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      deployed3Bots: [],
      wids : [],
    };
  },
  methods: {
    open(record) {
      this.selected = record;
      this.dialogs.info = true;
    },
    delete3Bot(wids) {
      this.wids = wids;
      this.dialogs.cancelWorkload = true;
    },
    openChatflow() {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: this.threebot_data.type },
      });
    },
    getDeployedSolutions() {
      this.$api.solutions
        .getDeployed()
        .then((response) => {
          this.deployed3Bots = [...response.data.data];
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
  mounted() {
    this.getDeployedSolutions();
  },
};
</script>
