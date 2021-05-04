<template>
  <div>
    <base-component title="MY VDCs" icon="mdi-clipboard-list-outline">
      <template #actions>
        <v-btn color="primary" text @click.stop="openChatflow('new_vdc')">
          <v-icon left>mdi-plus</v-icon>Add a new VDC
        </v-btn>
      </template>
      <div class="mt-5">
        <v-data-table
          :loading="loading"
          :headers="headersvdcs"
          :items="deployedvdcs"
          class="elevation-1"
        >
          <template slot="no-data">No VDC instances available</template>
          <template v-slot:item.id="{ item }">
            <div>{{ item.id }}</div>
          </template>
          <template v-slot:item.name="{ item }">
            {{ item.vdc_name }}
          </template>
          <template v-slot:item.package="{ item }">
            <div :class="`${item.class}`">{{ item.flavor }}</div>
          </template>
          <template v-slot:item.expiration="{ item }">
            <div :class="`${item.class}`">{{ item.expiration }}</div>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-tooltip top v-if="item.threebot.domain!==null">
              <template v-slot:activator="{ on, attrs }">
                <a
                  style="text-decoration: none"
                  :href="`https://${item.threebot.domain}/vdc_dashboard`"
                  target="_blank"
                >
                  <v-icon v-bind="attrs" v-on="on" color="primary"
                    >mdi-web</v-icon
                  >
                </a>
              </template>
              <span>Go to my VDC</span>
            </v-tooltip>
            <v-tooltip top v-else-if="item.threebot.domain===null">
              <template v-slot:activator="{ on, attrs }">
                  <v-icon v-bind="attrs" v-on="on" color="primary"
                    >mdi-access-point-network-off</v-icon
                  >
              </template>
              <span>There's an error reaching this VDC. Please wait if this VDC is deploying or
                contact support if it is already deployed.</span>
            </v-tooltip>
            <v-tooltip top>
              <template v-slot:activator="{ on, attrs }">
                <v-icon
                  v-bind="attrs"
                  v-on="on"
                  class="px-4"
                  @click="openWalletInfo(item.vdc_name)"
                  color="primary"
                  >mdi-wallet</v-icon
                >
              </template>
              <span>Show Wallet Info</span>
            </v-tooltip>
            <v-tooltip top>
              <template v-slot:activator="{ on, attrs }">
                <v-btn icon @click.stop="deleteVDC(item.vdc_name)">
                  <v-icon v-bind="attrs" v-on="on" color="#810000"
                    >mdi-delete</v-icon
                  >
                </v-btn>
              </template>
              <span>Delete</span>
            </v-tooltip>
          </template>
        </v-data-table>
      </div>
    </base-component>
    <wallet-info
      v-if="selected"
      v-model="dialogs.wallet"
      :vdcname="selected"
    ></wallet-info>
    <delete-vdc
      v-if="selectedvdc"
      v-model="dialogs.delete"
      :vdcname="selectedvdc"
    ></delete-vdc>
  </div>
</template>

<script>
module.exports = {
  components: {
    "wallet-info": httpVueLoader("./Wallet.vue"),
    "delete-vdc": httpVueLoader("./Delete.vue"),
  },
  data() {
    return {
      loading: true,
      headersvdcs: [
        { text: "ID", value: "id" },
        { text: "Name", value: "name" },
        { text: "Package", value: "package" },
        { text: "Expiration", value: "expiration" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      deployedvdcs: [],
      dialogs: {
        wallet: false,
        delete: false,
      },
      selected: null,
      selectedvdc: null,
      price: null,
    };
  },
  methods: {
    openChatflow(topic, tname = "") {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: topic, tname: tname },
      });
    },
    openWalletInfo(name) {
      this.selected = name;
      this.dialogs.wallet = true;
    },
    getDeployedSolutions() {
      const DURATION_MAX = 9223372036854775807;
      let today = new Date();
      let alert_time = new Date();
      alert_time.setDate(today.getDate() + 2);

      this.$api.solutions
        .listVdcs()
        .then((response) => {
          let deployments = [...response.data];
          for (let i = 0; i < deployments.length; i++) {
            deployedvdc = deployments[i];
            deployedvdc.alert = false;
            if (deployedvdc.expiration < DURATION_MAX) {
              let expiration = new Date(deployedvdc.expiration * 1000);
              deployedvdc.expiration = expiration.toLocaleString("en-GB");
              if (expiration < alert_time) {
                deployedvdc.alert = true;
              }
            } else {
              deployedvdc.expiration = "-";
            }
          }
          this.deployedvdcs = deployments.map((item, index) => ({
            id: index + 1,
            ...item,
          }));
        })
        .finally(() => {
          this.loading = false;
        });
    },
    deleteVDC(name) {
      this.selectedvdc = name;
      this.dialogs.delete = true;
    },
  },
  mounted() {
    this.getDeployedSolutions();
  },
};
</script>
