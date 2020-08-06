<template>
  <div>
    <base-section title="Pools" icon="mdi-cloud" :loading="loading">
      <v-data-table :items-per-page="5" :headers="headers" :items="pools" :footer-props="{'disable-items-per-page': true}">
          <template v-slot:item.node_ids="{ item }">
            {{ item.node_ids.length }}
          </template>
          <template v-slot:item.active_workload_ids="{ item }">
            {{ item.active_workload_ids.length }}
          </template>
      </v-data-table>
    </base-section>
  </div>
</template>

<script>
  module.exports = {
    data () {
      return {
        loading: false,
        selected: null,
        dialog: false,
        pools: [],
        headers: [
          {text: "ID", value: "pool_id"},
          {text: "CU", value: "cus"},
          {text: "SU", value: "sus"},
          {text: "ACU", value: "active_cu"},
          {text: "ASU", value: "active_su"},
          {text: "Nodes", value: "node_ids"},
          {text: "Workloads", value: "active_workload_ids"},
        ]
      }
    },
    methods: {
      getPools () {
        this.loading = true
        this.$api.solutions.getPools().then((response) => {
          this.pools = JSON.parse(response.data).data
        }).finally (() => {
          this.loading = false
        })
      }
    },
    mounted () {
      this.getPools()
    }
  }
</script>
