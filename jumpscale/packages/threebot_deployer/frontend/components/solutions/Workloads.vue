<template>
  <div>
    <base-component
      title="MY 3BOTS"
      icon="mdi-clipboard-list-outline"
      :loading="loading"
    >
      <template #actions>
        <v-btn color="primary" text @click.stop="openChatflow('threebot')">
          <v-icon left>mdi-plus</v-icon>New
        </v-btn>
      </template>
      <div class="mt-5">
        <template>
          <deployer-data-table
            :deployed="deployed3Bots"
            :headers="headers3Bots"
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
      headers3Bots: [
        { text: "Name", value: "name" },
        { text: "State", value: "state"},
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
            deployed3Bot.alert = false;
            if (deployed3Bot.expiration < DURATION_MAX) {
              let expiration = new Date(deployed3Bot.expiration * 1000);
              deployed3Bot.expiration = expiration.toLocaleString("en-GB");
              if (expiration < alert_time) {
                deployed3Bot.alert = true;
              }
            } else {
              deployed3Bot.expiration = "-";
            }
          }
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
