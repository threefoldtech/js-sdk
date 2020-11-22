<template>
  <div>
    <div class="actions mb-3">
      <h1 class="d-inline" color="primary" text>{{ $route.name }}</h1>
      <v-btn class="float-right p-4" color="primary" text>
        <v-icon left>mdi-plus</v-icon>Add node
      </v-btn>
    </div>

    <v-data-table
      :loading="loading"
      :headers="headers"
      :items="zdbData"
      class="elevation-1"
    >
      <template slot="no-data">No VDC instances available</template>
      <template v-slot:item.wid="{ item }">
        <div>{{ item.wid }}</div>
      </template>

      <template v-slot:item.node="{ item }">
        <div>{{ item.node_id }}</div>
      </template>

      <template v-slot:item.size="{ item }">
        <div>{{ item.size }}</div>
      </template>

      <template v-slot:item.actions="{ item }">
        <v-tooltip top>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="deleteNode(item)">
              <v-icon v-bind="attrs" v-on="on" color="#810000"
                >mdi-delete</v-icon
              >
            </v-btn>
          </template>
          <span>Destroy</span>
        </v-tooltip>
      </template>
    </v-data-table>
    <cancel-workload
      v-if="selected"
      v-model="dialogs.cancelWorkload"
      :data="selected"
    ></cancel-workload>
  </div>
</template>


<script>
module.exports = {
  name: "S3",
  components: {
    "cancel-workload": httpVueLoader("../solutions/Delete.vue"),
  },
  data() {
    return {
      dialogs: {
        cancelWorkload: false,
      },
      selected: null,
      headers: [
        { text: "WID", value: "wid" },
        { text: "Node", value: "node" },
        { text: "Size", value: "size" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      loading: false,
      vdc: {
        s3: {
          subdomain: "s3-testvdc9-testoooo09.tfgw-testnet-01.gateway.tf",
          healer_subdomain:
            "s3-testvdc9-testoooo09-healing.tfgw-testnet-01.gateway.tf",
          minio: {
            ip_address: "10.200.2.3",
            wid: 506628,
            node_id: "DNav25NSCpx8NHwX11CUoUMsr2VW42sGoFCx6dtxyMV9",
            pool_id: 5695,
          },
          zdbs: [
            {
              wid: 506612,
              node_id: "8BFWcddW79cawvjnuUMw8M5s9FqS3pHhMHvzn3pgCUiB",
              size: 67,
              pool_id: 5695,
            },
            {
              wid: 506613,
              node_id: "6m9gFPTYLRiCH7FD8yU5VWwXZdfegKUvXZgrJoS1EJfQ",
              size: 34,
              pool_id: 5695,
            },
            {
              wid: 506614,
              node_id: "3dAnxcykEDgKVQdTRKmktggL2MZbm3CPSdS9Tdoy4HAF",
              size: 45,
              pool_id: 5695,
            },
          ],
          api_proxy: {
            reverse_proxy: {
              wid: 506631,
              node_id: "6RZfnjuXVLFdtZh218hn4BLzsoKkTVpweqWECk5YUKud",
              pool_id: 5568,
            },
            subdomain: {
              wid: 506630,
              node_id: "6RZfnjuXVLFdtZh218hn4BLzsoKkTVpweqWECk5YUKud",
              pool_id: 5568,
            },
            nginx: {
              wid: 506640,
              node_id: "2tzdPqM5xrFHkn264GHyUzXQda9UxFGcWMR9BeN54FTi",
              pool_id: 5695,
            },
          },
          healer_proxy: {
            reverse_proxy: {
              wid: 506643,
              node_id: "6RZfnjuXVLFdtZh218hn4BLzsoKkTVpweqWECk5YUKud",
              pool_id: 5568,
            },
            subdomain: {
              wid: 506642,
              node_id: "6RZfnjuXVLFdtZh218hn4BLzsoKkTVpweqWECk5YUKud",
              pool_id: 5568,
            },
            nginx: {
              wid: 506644,
              node_id: "DNav25NSCpx8NHwX11CUoUMsr2VW42sGoFCx6dtxyMV9",
              pool_id: 5695,
            },
          },
        },
        kubernetes: [
          {
            role: "master",
            ip_address: "10.200.2.2",
            size: 1,
            wid: 506619,
            node_id: "DNav25NSCpx8NHwX11CUoUMsr2VW42sGoFCx6dtxyMV9",
            pool_id: 5695,
          },
          {
            role: "worker",
            ip_address: "10.200.3.2",
            size: 1,
            wid: 506626,
            node_id: "8BFWcddW79cawvjnuUMw8M5s9FqS3pHhMHvzn3pgCUiB",
            pool_id: 5695,
          },
        ],
      },
    };
  },
  methods: {
    deleteNode(record) {
      this.selected = record;
      this.dialogs.cancelWorkload = true;
    },
  },
  computed: {
    zdbData() {
      return this.vdc.s3.zdbs;
    },
  },
};
</script>

<style scoped>
h1 {
  color: #1b4f72;
}
</style>