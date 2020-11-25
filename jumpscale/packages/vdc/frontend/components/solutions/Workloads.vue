<template>
  <div>
    <base-component
      title="MY VDCs"
      icon="mdi-clipboard-list-outline"
      :loading="loading"
    >
      <template #actions>
        <v-btn color="primary" text>
          <v-icon left>mdi-plus</v-icon>Add a new VDC
        </v-btn>
      </template>
      <div class="mt-5">
        <template>
          <deployer-data-table
            :deployed="deployedvdcs"
            :headers="headers3Bots"
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
      threebot_data: APPS["threebot"],
      loading: true,
      headers3Bots: [
        { text: "ID", value: "id" },
        { text: "Name", value: "name" },
        { text: "Package", value: "package" },
        { text: "Expiration", value: "expiration" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      deployedvdcs: [
        {
          vdc_name: "testvdc9",
          owner_tname: "testoooo09",
          solution_uuid: "0b5754eb1e324663971746fd2e78511a",
          identity_tid: 2728,
          flavor: "silver",
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
          created: 1605698806,
          updated: 1605698806,
          expiration: 1608290806,
        },
      ],
    };
  },
  methods: {
    openChatflow(type, tname = "") {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: type, tname: tname },
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
        .getAllThreebots()
        .then((response) => {
          this.deployedvdcs = [...response.data.data];
          for (let i = 0; i < this.deployedvdcs.length; i++) {
            deployed3Bot = this.deployedvdcs[i];
            deployed3Bot.alert = false;
            if (deployed3Bot.expiration < DURATION_MAX) {
              let expiration = new Date(deployed3Bot.expiration * 1000);
              deployed3Bot.expiration = expiration.toLocaleString("en-GB");
              if (expiration < alert_time) {
                deployed3Bot.alert = true;
              }
            } else {
              deployed3Bot.expiration = "-";
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
