<template>
  <div>
      <template>
        <v-data-table
          :loading="loading"
          :headers="headers"
          :items="data"
          class="elevation-1"
        >
          <template slot="no-data">No 3Bot instances available</p></template>
          <template v-slot:item.domain="{ item }" >
            <a v-if="deployed3botsStatus[item.Status] === 3"  :href="`https://${item.Domain}/admin`">{{item.Domain}}</a>
          </template>
          <template v-slot:item.Expiration="{ item }">
            <div :class="`${item.class}`">{{ item.Expiration }}</div>
          </template>
          <template v-slot:item.Status="{ item }">
            <div :class="`${item.class}`">{{ item.Status }}</div>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-tooltip top v-if="deployed3botsStatus[item.Status] === 3" >
              <template v-slot:activator="{ on, attrs }">
                <v-btn icon :href="`https://${item.Domain}/admin`">
                  <v-icon v-bind="attrs" v-on="on" color="primary">mdi-web</v-icon>
                </v-btn>
              </template>
              <span>Open in browser</span>
            </v-tooltip>
            <v-tooltip top  v-if="deployed3botsStatus[item.Status] !== 1">
              <template v-slot:activator="{ on, attrs }">
                    
                <v-btn icon @click.stop="delete3Bot(item)">
                  <v-icon v-bind="attrs" v-on="on" color="#810000">mdi-delete</v-icon>
                </v-btn>
              </template>
              <span>Destroy</span>
            </v-tooltip>
            <v-tooltip top>
              <template v-slot:activator="{ on, attrs }">
                <v-btn icon @click.stop="open(item)">
                  <v-icon v-bind="attrs" v-on="on" color="#206a5d">mdi-information-outline</v-icon>
                </v-btn>
              </template>
              <span>Show Information</span>
            </v-tooltip>
            <v-tooltip top v-if="deployed3botsStatus[item.Status] == 3">
              <template v-slot:activator="{ on, attrs }">
                <v-btn icon @click.stop="stop3Bot(item)">
                  <v-icon v-bind="attrs" v-on="on" color="#206a5d">mdi-stop-circle</v-icon>
                </v-btn>
              </template>
              <span>Stop</span>
            </v-tooltip>
            <v-tooltip top v-if="deployed3botsStatus[item.Status] !== 3">
              <template v-slot:activator="{ on, attrs }">
                <v-btn icon @click.stop="start3Bot(item)">
                  <v-icon v-bind="attrs" v-on="on" color="#206a5d">mdi-reload</v-icon>
                </v-btn>
              </template>
              <span>Start</span>
            </v-tooltip>
          </template>
        </v-data-table>
      </template>
    <solution-info v-if="selected" v-model="dialogs.info" :data="selected"></solution-info>
    <cancel-workload v-if="selected" v-model="dialogs.cancelWorkload" :data="selected"></cancel-workload>
    <stop-workload v-if="selected" v-model="dialogs.stopWorkload" :data="selected"></stop-workload>
  </div>
</template>

<script>
module.exports = {
  props: ["data", "headers", "loading"],
  components: {
    "solution-info": httpVueLoader("./Info.vue"),
    "cancel-workload": httpVueLoader("./Delete.vue"),
    "stop-workload": httpVueLoader("./Stop.vue"),
  },
  data() {
    return {
      dialogs: {
        info: false,
        cancelWorkload: false,
        stopWorkload: false,
        startWorkload: false,
      },
      selected: null,
      deployed3botsStatus: {
        Destroyed: 1,
        Stopped: 2,
        Running: 3,
      },
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
    stop3Bot(record) {
      this.selected = record;
      this.dialogs.stopWorkload = true;
    },
    start3Bot(record) {
      this.selected = record;
      this.dialogs.startWorkload = true;
      this.openChatflow("restart_threebot", this.selected.Name);
    },
    openChatflow(type, tname = "") {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: type, tname: tname },
      });
    },
  },
};
</script>