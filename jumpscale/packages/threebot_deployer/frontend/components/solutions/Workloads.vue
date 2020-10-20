<template>
  <div>
    <base-component
      title="MY 3BOTS"
      icon="mdi-clipboard-list-outline"
      :loading="loading"
    >
      <template #actions>
        <v-btn color="primary" text @click.stop="openChatflow('extend')">
          <v-icon left>mdi-upload</v-icon>Extend 3Bot
        </v-btn>
        <v-btn color="primary" text @click.stop="openChatflow('threebot')">
          <v-icon left>mdi-plus</v-icon>New
        </v-btn>
      </template>
      <!-- Running 3bots -->
      <div class="mt-5">
        <div>
          <h4 class="my-4">RUNNING</h4>
        </div>
        <template>
          <deployer-data-table
            :data="running3bots"
            :headers="headersRunning3obts"
            :loading="loading"
          >
          </deployer-data-table>
        </template>
      </div>

      <!-- Stopped 3bots -->
      <div class="mt-5">
        <div>
          <h4 class="my-4">STOPPED</h4>
        </div>

        <template>
          <deployer-data-table
            :data="stopped3bots"
            :headers="headersNotRunning3obts"
            :loading="loading"
          >
          </deployer-data-table>
        </template>
      </div>
      <!-- Destroyed 3bots -->
      <div class="mt-5">
        <div>
          <h4 class="my-4">DESTROYED</h4>
        </div>
        <template>
          <deployer-data-table
            :data="destroyed3bots"
            :headers="headersNotRunning3obts"
            :loading="loading"
          >
          </deployer-data-table>
        </template>
      </div>
    </base-component>
  </div>
</template>

<script>
module.exports = {
  components: {
    "deployer-data-table": httpVueLoader("../base/Table.vue"),
  },
  data() {
    return {
      threebot_data: APPS["threebot"],
      loading: true,
      headersRunning3obts: [
        { text: "Name", value: "Name" },
        { text: "URL", value: "domain" },
        { text: "Expiration", value: "expiration" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      headersNotRunning3obts: [
        { text: "Name", value: "Name" },
        { text: "Status", value: "Status" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      deployed3Bots: [],
      running3bots: [],
      stopped3bots: [],
      destroyed3bots: [],
    };
  },
  methods: {
    openChatflow(type, tname = "") {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: type, tname: tname },
      });
    },
    groupBy(list, keyGetter) {
      const map = new Map();
      list.forEach((item) => {
        const key = keyGetter(item);
        const collection = map.get(key);
        if (!collection) {
          map.set(key, [item]);
        } else {
          collection.push(item);
        }
      });
      return map;
    },
    getDeployedSolutions() {
      const DURATION_MAX = 9223372036854775807;
      let today = new Date();
      let alert_time = new Date();
      alert_time.setDate(today.getDate() + 2);
      this.$api.solutions
        .getAllThreebots()
        .then((response) => {
          this.deployed3Bots = [...response.data.data];
          for (let i = 0; i < this.deployed3Bots.length; i++) {
            deployed3Bot = this.deployed3Bots[i];
            if (deployed3Bot.Expiration < DURATION_MAX) {
              let expiration = new Date(deployed3Bot.Expiration * 1000);
              deployed3Bot.Expiration = expiration.toLocaleString("en-GB");
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
        })
        .finally(() => {
          this.loading = false;
          this.deployed3Botsgrouped = this.groupBy(
            this.deployed3Bots,
            (bot) => bot.Status
          );
          this.running3bots = this.deployed3Botsgrouped.get("Running");
          this.stopped3bots = this.deployed3Botsgrouped.get("Stopped");
          this.destroyed3bots = this.deployed3Botsgrouped.get("Destroyed");
        });
    },
  },
  mounted() {
    this.getDeployedSolutions();
  },
};
</script>