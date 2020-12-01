<template>
  <div>
    <base-component
      title="MY VDCs"
      icon="mdi-clipboard-list-outline"
      :loading="loading"
    >
      <template #actions>
        <v-btn color="primary" text @click.stop='openChatflow("new_vdc")'>
          <v-icon left>mdi-plus</v-icon>Add a new VDC
        </v-btn>
      </template>
      <div class="mt-5">
        <template>
          <deployer-data-table
            :deployed="deployedvdcs"
            :headers="headersvdcs"
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
      loading: true,
      headersvdcs: [
        { text: "ID", value: "id" },
        { text: "Name", value: "name" },
        { text: "Package", value: "package" },
        { text: "Expiration", value: "expiration" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      deployedvdcs: [],
    };
  },
  methods: {
    openChatflow(topic, tname = "") {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: topic, tname: tname },
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
        .listVdcs()
        .then((response) => {
          this.deployedvdcs = [...response.data];
          for (let i = 0; i < this.deployedvdcs.length; i++) {
            deployedvdc = this.deployedvdcs[i];
            deployedvdc.alert = false;
            if (deployedvdc.expiration < DURATION_MAX) {
              let expiration = new Date(deployedvdc.expiration * 1000);
              deployedvdc.expiration = expiration.toLocaleString("en-GB");
              if (expiration < alert_time) {
                deployedvdc.alert = true;
              }
            } else {
              deployedvdc.expiration = "-";
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
