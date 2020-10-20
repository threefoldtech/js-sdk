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

      <template #default>
        <deployer-data-table
          :data="deployed3Bots"
          :headers="headers"
          :loading="loading"
        >
        </deployer-data-table>
      </template>
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
      headers: [
        { text: "Name", value: "Name" },
        { text: "URL", value: "domain" },
        { text: "Expiration", value: "expiration" },
        { text: "Status", value: "Status" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      deployed3Bots: [],
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
        });
    },
  },
  mounted() {
    this.getDeployedSolutions();
  },
};
</script>