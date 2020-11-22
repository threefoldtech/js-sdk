<template>
  <div>
    <div class="actions mb-3">
      <h1 class="d-inline" color="primary" text>{{ $route.name }}</h1>
      <v-btn class="float-right p-4" color="primary" text>
        <v-icon left>mdi-plus</v-icon>Add IP
      </v-btn>
    </div>

    <v-data-table
      :loading="loading"
      :headers="headers"
      :items="ipsData"
      class="elevation-1"
    >
      <template slot="no-data">No VDC instances available</template>
      <template v-slot:item.id="{ item }">
        <div>{{ item.id }}</div>
      </template>

      <template v-slot:item.ip="{ item }">
        <div>{{ item.ip }}</div>
      </template>

      <template v-slot:item.farm="{ item }">
        <div>{{ item.farm }}</div>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-tooltip top>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="deleteIP(item)">
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
    <solution-info
      v-if="selected"
      v-model="dialogs.info"
      :data="selected"
    ></solution-info>
  </div>
</template>

<script>
module.exports = {
  name: "IP",
  components: {
    "solution-info": httpVueLoader("../solutions/Info.vue"),
    "cancel-workload": httpVueLoader("../solutions/Delete.vue"),
  },
  data() {
    return {
      selected: null,
      dialogs: {
        info: false,
        cancelWorkload: false,
      },
      headers: [
        { text: "ID", value: "id" },
        { text: "IP Address", value: "ip" },
        { text: "Farm", value: "farm" },
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
        ips: [
          { id: 1, ip: "10.2.3.1", farm: "freefarm" },
          { id: 2, ip: "12.2.3.1", farm: "greenedge" },
        ],
      },
    };
  },
  methods: {
    open(record) {
      this.selected = record;
      this.dialogs.info = true;
    },
    deleteIP(record) {
      this.selected = record;
      this.dialogs.cancelWorkload = true;
    },
  },
  computed: {
    ipsData() {
      return this.vdc.ips;
    },
  },
};
</script>

<style scoped>
h1 {
  color: #1b4f72;
}
</style>