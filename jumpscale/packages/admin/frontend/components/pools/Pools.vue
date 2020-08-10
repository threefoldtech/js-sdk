<template>
  <div>
    <base-component title="Pools" icon="mdi-cloud" :loading="loading">
      <template #actions>
        <v-btn color="primary" text to="/solutions/pools_reservation">
          <v-icon left>mdi-cloud</v-icon> Create/Extend Pool
        </v-btn>
      </template>

      <template #default>
        <v-data-table :headers="headers" :items="pools" :footer-props="{'disable-items-per-page': true}" @click:row="open">
            <template v-slot:item.node_ids="{ item }">
            {{ item.node_ids.length }}
          </template>
          <template v-slot:item.active_workload_ids="{ item }">
            {{ item.active_workload_ids.length }}
          </template>
        </v-data-table>
      </template>
    </base-component>

    <pool-info v-model="dialog" :pool="selected"></pool-info>
  </div>
</template>


<script>
  module.exports = {
    components: {
      'pool-info': httpVueLoader("./Pool.vue")
    },
    data () {
      return {
        loading: false,
        selected: null,
        dialog: false,
        pools: [],
        headers: [
          {text: "ID", value: "pool_id"},
          {text: "Farm", value: "farm"},
          {text: "Expiration", value: "empty_at"},
          {text: "Compute Units", value: "cus"},
          {text: "Storage Units", value: "sus"},
          {text: "Active Compute Units", value: "active_cu"},
          {text: "Active Storage Units", value: "active_su"},
          {text: "Number of Nodes", value: "node_ids"},
          {text: "Number of Active Workloads", value: "active_workload_ids"},
        ]
      }
    },
    methods: {
      getPools () {
        this.loading = true
        this.$api.solutions.getPools().then((response) => {
          this.pools = JSON.parse(response.data).data
          for (let i = 0; i < this.pools.length; i++) {
            pool = this.pools[i];
            if (pool.empty_at < 9223372036854775807) {
              pool.empty_at = new Date(pool.empty_at * 1000).toLocaleString();
            } else {
              pool.empty_at = "-";
            }
          }
        }).finally (() => {
          this.loading = false
        })
      },
      open (pool) {
        this.selected = pool
        this.dialog = true
      },
    },
    mounted () {
      this.getPools()
    }
  }
</script>


<style scoped>
input {
  width: 50px;
}
.v-text-field {
  padding: 10px 0px !important;
}
</style>
