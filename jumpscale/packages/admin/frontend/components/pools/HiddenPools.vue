<template>
  <div>
    <base-dialog title="Hidden Pools" v-model="dialog" :loading="loading">
      <template #default>
        <v-data-table :headers="headers" :items="hidden_pools" :footer-props="{'disable-items-per-page': true}" @click:row="open">
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
      </template>
      <template #actions>
        <v-btn text @click="close">Close</v-btn>
      </template>
    </base-dialog>

    <pool-info v-model="pool_dialog" :pool="selected" :hidden="true"></pool-info>
  </div>
</template>


<script>
module.exports = {
  components: {
    'pool-info': httpVueLoader("./Pool.vue"),
  },
  props: ["hidden_pools"],
  mixins: [dialog],
  data () {
      return {
        selected: null,
        pool_dialog: false,
        headers: [
          {text: "ID", value: "pool_id"},
          {text: "Name", value: "name"},
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
      open (pool) {
        this.selected = pool
        this.pool_dialog = true
      }
  }
};
</script>
