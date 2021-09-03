<template>
  <div>
    <template>
      <v-data-table
        :loading="loading"
        :headers="headers"
        :items="filteredBots"
        class="elevation-1"
      >
        <template v-slot:body.prepend="{ headers }">
          <tr>
            <td></td>
            <td>
              <v-select
                v-model="filters.state"
                :items="states"
                clearable
                filled
                hide-details
                dense
                class="table-colomns-max"
              ></v-select>
            </td>
            <td></td>
          </tr>
        </template>
        <template slot="no-data">No 3Bot instances available</template>
        <template v-slot:item.domain="{ item }">
          <a
            v-if="
              deployed3botsStatus[item.state] === 3 ||
              deployed3botsStatus[item.state] === 4
            "
            :href="`https://${item.domain}/admin`"
            >{{ item.domain }}</a
          >
        </template>
        <template v-slot:item.expiration="{ item }">
          <div :class="`${item.class}`">{{ item.expiration }}</div>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-tooltip
            top
            v-if="
              deployed3botsStatus[item.state] == 3 ||
              deployed3botsStatus[item.state] == 4
            "
          >
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon @click.stop="stop3Bot(item)">
                <v-icon v-bind="attrs" v-on="on" color="#206a5d"
                  >mdi-stop-circle</v-icon
                >
              </v-btn>
            </template>
            <span>Stop</span>
          </v-tooltip>

          <v-tooltip
            top
            v-if="
              deployed3botsStatus[item.state] == 1 ||
              deployed3botsStatus[item.state] == 2
            "
          >
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon @click.stop="start3Bot(item)">
                <v-icon v-bind="attrs" v-on="on" color="#206a5d"
                  >mdi-reload</v-icon
                >
              </v-btn>
            </template>
            <span>Start</span>
          </v-tooltip>

          <v-tooltip top>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon @click.stop="open(item)">
                <v-icon v-bind="attrs" v-on="on" color="#206a5d"
                  >mdi-information-outline</v-icon
                >
              </v-btn>
            </template>
            <span>Show Information</span>
          </v-tooltip>

          <v-tooltip top v-if="deployed3botsStatus[item.state] !== 1">
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon @click.stop="delete3Bot(item)">
                <v-icon v-bind="attrs" v-on="on" color="#810000"
                  >mdi-delete</v-icon
                >
              </v-btn>
            </template>
            <span>Destroy</span>
          </v-tooltip>

          <v-tooltip top v-if="deployed3botsStatus[item.state] === 3">
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                icon
                :href="`https://${item.domain}/admin`"
                target="_blank"
              >
                <v-icon v-bind="attrs" v-on="on" color="primary"
                  >mdi-web</v-icon
                >
              </v-btn>
            </template>
            <span>Open in browser</span>
          </v-tooltip>

          <v-tooltip top v-else-if="deployed3botsStatus[item.state] == 4">
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                icon
                :href="`https://${item.domain}/admin`"
                target="_blank"
              >
                <v-icon v-bind="attrs" v-on="on" color="#810000"
                  >mdi-access-point-network-off</v-icon
                >
              </v-btn>
            </template>
            <span
              >There's an error reaching this 3Bot. Please restart the 3Bot or
              contact support.</span
            >
          </v-tooltip>

          <v-tooltip top v-if="deployed3botsStatus[item.state] == 2">
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon @click.stop="change3BotLocation(item)">
                <v-icon v-bind="attrs" v-on="on" color="#206a5d"
                  >mdi-map-marker-radius</v-icon
                >
              </v-btn>
            </template>
            <span>Change location</span>
          </v-tooltip>

          <v-tooltip top v-if="deployed3botsStatus[item.state] == 2">
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon @click.stop="change3BotSize(item)">
                <v-icon v-bind="attrs" v-on="on" color="#206a5d"
                  >mdi-arrow-expand-all</v-icon
                >
              </v-btn>
            </template>
            <span>Change size</span>
          </v-tooltip>

          <v-tooltip top v-if="item.alert === true">
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon>
                <v-icon v-bind="attrs" v-on="on" color="#810000"
                  >mdi-alert</v-icon
                >
              </v-btn>
            </template>
            <span
              >This 3Bot expires in less than 2 days. Please go to your admin
              dashboard and extend pool {{ item.compute_pool }}</span
            >
          </v-tooltip>
        </template>
      </v-data-table>
    </template>
    <solution-info
      v-if="selected"
      v-model="dialogs.info"
      :data="selected"
    ></solution-info>
    <cancel-workload
      v-if="selected"
      v-model="dialogs.cancelWorkload"
      :data="selected"
    ></cancel-workload>
    <stop-workload
      v-if="selected"
      v-model="dialogs.stopWorkload"
      :data="selected"
    ></stop-workload>
  </div>
</template>

<script>
module.exports = {
  props: ["deployed", "headers", "loading"],
  components: {
    "solution-info": httpVueLoader("../solutions/Info.vue"),
    "cancel-workload": httpVueLoader("../solutions/Delete.vue"),
    "stop-workload": httpVueLoader("../solutions/Stop.vue"),
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
        DELETED: 1,
        STOPPED: 2,
        RUNNING: 3,
        ERROR: 4,
      },
      states: ["RUNNING", "ERROR", "STOPPED", "DELETED"],
      filters: {
        state: null,
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
      this.openChatflow("restart_threebot", this.selected.name);
    },
    change3BotSize(record) {
      this.openChatflow("change_size", record.name);
    },
    change3BotLocation(record) {
      this.openChatflow("change_location", record.name);
    },
    openChatflow(type, tname = "") {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: type, tname: tname },
      });
    },
  },
  computed: {
    filteredBots() {
      return this.deployed.filter((record) => {
        let result = [];
        Object.keys(this.filters).forEach((key) => {
          result.push(
            !this.filters[key] ||
              String(record[key]).includes(this.filters[key])
          );
        });
        return result.every(Boolean);
      });
    },
  },
};
</script>
