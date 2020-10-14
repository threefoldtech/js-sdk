<template>
  <div>
    <base-component title="Capacity Pools" icon="mdi-cloud">
      <template #actions>
        <v-btn color="primary" text to="/solutions/pools">
          <v-icon left>mdi-cloud</v-icon>Create/Extend Pool
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
          <template v-slot:item.empty_at="{ item }">
            <div :class="`${item.class}`">{{ item.empty_at }}</div>
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
        { text: "Compute Units", value: "cus" },
        { text: "Storage Units", value: "sus" },
        { text: "Active Compute Units", value: "active_cu" },
        { text: "Active Storage Units", value: "active_su" },
        { text: "Number of Nodes", value: "node_ids" },
        { text: "Number of Active Workloads", value: "active_workload_ids" },
      ],
    };
  },
  computed: {
    pools: function () {
      return this.all_pools.filter((pool) => !pool.hidden || this.show_hidden && pool.hidden);
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
              pool.empty_at = pool_expiration.toLocaleString('en-GB');
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
      if (this.show_hidden){
        this.toggle_button_text = "Mask hidden pools"
        this.headers.push({ text: "Hidden", value: "hidden"})
      }else{
        this.toggle_button_text = "Show hidden pools"
        this.headers.pop();
      }
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
