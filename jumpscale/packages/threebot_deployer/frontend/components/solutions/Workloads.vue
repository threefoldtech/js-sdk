<template>
  <div>
    <base-component title="MY 3BOTS" icon="mdi-clipboard-list-outline" :loading="loading">
      <template #actions>
        <v-btn color="primary" text @click.stop="openChatflow('extend')">
          <v-icon left>mdi-upload</v-icon>Extend 3Bot
        </v-btn>
        <v-btn color="primary" text @click.stop="openChatflow('threebot')">
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
          <template slot="no-data">No 3Bot instances available</p></template>
          <template v-slot:item.domain="{ item }">
            <a :href="`https://${item.Domain}/admin`">{{item.Domain}}</a>
          </template>
          <template v-slot:item.Expiration="{ item }">
            <div :class="`${item.class}`">{{ item.Expiration }}</div>
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
                <v-btn icon @click.stop="delete3Bot(item)">
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
    <cancel-workload v-if="selected" v-model="dialogs.cancelWorkload" :data="selected"></cancel-workload>
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
        { text: "Expiration", value: "expiration" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      deployed3Bots: [],
    };
  },
  methods: {
    open(record) {
      this.selected = record;
      this.dialogs.info = true;
    },
    delete3Bot(record) {
      this.selected = record;
      this.dialogs.cancelWorkload = true;
    },
    openChatflow(type) {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: type },
      });
    },
    getDeployedSolutions() {
      const DURATION_MAX = 9223372036854775807;
      let today = new Date();
      let alert_time = new Date();
      alert_time.setDate(today.getDate() + 2);
      this.$api.solutions
        .getDeployed()
        .then((response) => {
          this.deployed3Bots = [...response.data.data];
          for (let i = 0; i < this.deployed3Bots.length; i++) {
            deployed3Bot = this.deployed3Bots[i];
            if (deployed3Bot.Expiration < DURATION_MAX) {
              let expiration = new Date(deployed3Bot.Expiration * 1000);
              deployed3Bot.Expiration = expiration.toLocaleString();
              if (expiration < today) {
                deployed3Bot.class = "red--text";
                deployed3Bot.Expiration = "EXPIRED";
              } else if (expiration < alert_time) {
                deployed3Bot.class = "red--text";
              } else {
                deployed3Bot.class = "";
              }
            } else {
              deployed3Bot.Expiration = "-";
            }
          }
        }).finally(() => {
          this.loading = false;
        });
    },
  },
  mounted() {
    this.getDeployedSolutions();
  },
};
</script>
