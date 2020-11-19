<template>
  <v-container fluid class="grey lighten-5 mt-5">
    <v-row no-gutters>
      <v-col cols="6" md="2">
        <v-card width="256">
          <sidebar :name="name" :vdc="vdc" />
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="10">
        <router-view></router-view>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
module.exports = {
  name: "VDC",
  components: {
    sidebar: httpVueLoader("../base/Sidebar.vue"),
  },
  props: ["name"],
  data() {
    return {
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
              pool_id: 5695,
            },
            {
              wid: 506613,
              node_id: "6m9gFPTYLRiCH7FD8yU5VWwXZdfegKUvXZgrJoS1EJfQ",
              pool_id: 5695,
            },
            {
              wid: 506614,
              node_id: "3dAnxcykEDgKVQdTRKmktggL2MZbm3CPSdS9Tdoy4HAF",
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
};
</script>
