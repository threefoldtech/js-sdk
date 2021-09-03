<template>
  <div>
    <base-component title="Capacity Pools" icon="mdi-cloud">
      <template #actions>
        <v-btn color="primary" text to="/solutions/pools">
          <v-icon left>mdi-cloud</v-icon>Create Pool
        </v-btn>
        <v-btn color="primary" text @click="toggleHiddenPools">
          <v-icon left>mdi-eye-off</v-icon>{{toggle_button_text}}
        </v-btn>
      </template>

      <template #default>
        <v-data-table :headers="headers" :loading="loading" :items="pools.reverse()" @click:row="open">
          <template slot="no-data">No pools available</p></template>
          <template v-slot:item.node_ids="{ item }">{{ item.node_ids.length }}</template>
          <template v-slot:item.active_workload_ids="{ item }">{{ item.active_workload_ids.length }}</template>
          <template v-slot:item.cus="{ item }">{{ ( item.active_cu * (30*24*60*60) ).toFixed(1) }} / {{ item.cus.toFixed(1) }} </template>
          <template v-slot:item.sus="{ item }">{{ ( item.active_su * (30*24*60*60) ).toFixed(1) }} / {{ item.sus.toFixed(1) }} </template>
          <template v-slot:item.ipv4us="{ item }">{{ ( item.active_ipv4 * (30*24*60*60) ).toFixed(1) }} / {{ item.ipv4us.toFixed(1) }} </template>
          <template v-slot:item.empty_at="{ item }">
            <div :class="`${item.class}`">{{ item.empty_at }}</div>
          </template>
          <template v-slot:item.name="{item}"> {{ item.name }}</template>
          <template v-slot:item.actions="{ item }" #actions>
              <v-tooltip top>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn icon @click="openChatflow(item.pool_id)">
                      <v-icon v-bind="attrs" v-on="on" color=primary>mdi-resize</v-icon>
                    </v-btn>
                  </template>
                  <span>Extend pool</span>
                </v-tooltip>
          </template>
        </v-data-table>
      </template>
    </base-component>

    <pool-info v-model="dialog" v-if="selected" :pool="selected"></pool-info>
  </div>
</template>


<script>
module.exports = {
  components: {
    "pool-info": httpVueLoader("./Pool.vue"),
  },
  data() {
    return {
      loading: true,
      selected: null,
      dialog: false,
      hidden_dialog: false,
      show_hidden: false,
      toggle_button_text: "Show hidden pools",
      all_pools: [],
      headers: [
        { text: "ID", value: "pool_id" },
        { text: "Name", value: "name" },
        { text: "Farm", value: "farm" },
        { text: "Expiration", value: "empty_at" },
        { text: "Active CUs/Total CUs", value: "cus" },
        { text: "Active SUs/Total SUs", value: "sus" },
        { text: "Active IPv4Us/Total IPv4Us", value: "ipv4us" },
        { text: "# Nodes", value: "node_ids" },
        { text: "# Active Workloads", value: "active_workload_ids" },
        { text: "Actions", value: "actions" },
      ],
    };
  },
  computed: {
    pools: function () {
      return this.all_pools.filter(
        (pool) => !pool.hidden || (this.show_hidden && pool.hidden)
      );
    },
  },
  methods: {
    getPools(include_hidden) {
      this.loading = true;
      const DURATION_MAX = 9223372036854775807;

      let today = new Date();
      let alert_time = new Date();
      alert_time.setDate(today.getDate() + 2);

      this.$api.solutions
        .getPools(true) //get all pools, shown and hidden
        .then((response) => {
          this.all_pools = JSON.parse(response.data).data;
          for (let i = 0; i < this.all_pools.length; i++) {
            pool = this.all_pools[i];
            if (pool.empty_at < DURATION_MAX) {
              let pool_expiration = new Date(pool.empty_at * 1000);
              pool.empty_at = pool_expiration.toLocaleString("en-GB");
              if (pool_expiration < today) {
                pool.class = "red--text";
                pool.empty_at = "EXPIRED";
              } else if (pool_expiration < alert_time) {
                pool.class = "red--text";
              } else {
                pool.class = "";
              }
            } else {
              pool.empty_at = "-";
            }
          }
        })
        .finally(() => {
          this.loading = false;
        });
    },
    open(pool) {
      this.selected = pool;
      this.dialog = true;
    },
    toggleHiddenPools() {
      this.show_hidden = !this.show_hidden;
      console.log("show hidden pool: " + this.show_hidden);
      if (this.show_hidden) {
        this.toggle_button_text = "Mask hidden pools";
        this.headers.push({ text: "Hidden", value: "hidden" });
      } else {
        this.toggle_button_text = "Show hidden pools";
        this.headers.pop();
      }
    },
    openChatflow(pool_id) {
      let queryparams = { pool_id: pool_id };
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: "extend_pools", queryparams: queryparams },
      });
    },
  },
  mounted() {
    this.getPools();
  },
};
</script>


<style scoped>
input {
  width: 50px;
}
.v-text-field {
  padding: 10px 0px !important;
}
.v-data-table tr {
  cursor: pointer;
}
</style>
