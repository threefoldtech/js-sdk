<template>
  <div>
    <base-section title="Pools" icon="mdi-cloud" :loading="loading">
      <v-data-table :items-per-page="5" :headers="headers" :items="pools" :footer-props="{'disable-items-per-page': true}" @click:row="open" class="row-pointer">
          <template slot="no-data">No pools available</p></template>
          <template v-slot:item.node_ids="{ item }">
            {{ item.node_ids.length }}
          </template>
          <template v-slot:item.active_workload_ids="{ item }">
            {{ item.active_workload_ids.length }}
          </template>
          <template v-slot:item.empty_at="{ item }">
            <div :class="`${item.class}`">{{ item.empty_at }}</div>
          </template>
      </v-data-table>
    </base-section>
    <pool-info v-if="selected" v-model="dialog" :pool="selected"></pool-info>
  </div>
</template>

<script>
  module.exports = {
    components: {
      'pool-info': httpVueLoader("../pools/Pool.vue")
    },
    data () {
      return {
        loading: false,
        selected: null,
        dialog: false,
        pools: [],
        headers: [
          {text: "ID", value: "pool_id"},
          {text: "Name", value: "name"},
          {text: "Farm", value: "farm"},
          {text: "Expiration", value: "empty_at"}
        ]
      }
    },
    methods: {
      getPools () {
        this.loading = true
        let today = new Date();
        let alert_time = new Date()
        alert_time.setDate(today.getDate() + 2)
        this.$api.solutions.getPools().then((response) => {
          this.pools = JSON.parse(response.data).data
          for (let i = 0; i < this.pools.length; i++) {
            pool = this.pools[i];
            if (pool.empty_at < 9223372036854775807) {
              let pool_expiration = new Date(pool.empty_at * 1000);
              pool.empty_at = pool_expiration.toLocaleString('en-GB');
              if (pool_expiration < today){
                pool.class = "red--text";
                pool.empty_at = "EXPIRED"
              } else if (pool_expiration < alert_time && pool_expiration > today) {
                pool.class = "red--text";
              } else {
                pool.class = "";
              }
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
.v-data-table tr {
  cursor: pointer;
}
</style>
