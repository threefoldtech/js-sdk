<template>
  <v-container fluid class="grey lighten-5 mt-5">
    <v-tabs
      v-model="activetab"
      class="text--left"
      background-color="transparent"
      vertical
    >
      <v-tab v-for="(tab, index) in tabs" :key="index">
        <v-icon left>{{ tab.icon }} </v-icon>
        {{ tab.title }}
      </v-tab>

      <v-tab-item class="ml-2">
        <v-card flat>
          <kubernetes
            :vdc="vdc"
            :loading="tableloading"
            @reload-vdcinfo="vdcInfo"
          ></kubernetes>
        </v-card>
      </v-tab-item>
      <v-tab-item class="ml-2">
        <v-card flat>
          <virtual-machine :vmachines="vdc ? vdc.vmachines : []" :tableloading="tableloading"></virtual-machine>
        </v-card>
      </v-tab-item>
      <v-tab-item class="ml-2">
        <v-card flat>
          <s3
            :vdc="vdc"
            :tableloading="tableloading"
            @reload-vdcinfo="vdcInfo"
          ></s3>
        </v-card>
      </v-tab-item>
      <v-tab-item class="ml-2">
        <v-card flat>
          <wallet
            :wallet="wallet"
            :price="price"
            :expirationdata="expirationData"
          ></wallet>
        </v-card>
      </v-tab-item>
      <v-tab-item class="ml-2">
        <v-card flat>
          <backups :vdc="vdc" :loading="tableloading"></backups>
        </v-card>
      </v-tab-item>
      <v-tab-item class="ml-2">
        <v-card flat>
          <alerts :alertid="parseInt(alertid)"></alerts>
        </v-card>
      </v-tab-item>

      <v-tab-item class="ml-2">
        <v-card flat>
          <admins :vdc="vdc" :loading="tableloading"></admins>
        </v-card>
      </v-tab-item>

      <v-tab-item class="ml-2">
        <v-card flat>
          <api-keys></api-keys>
        </v-card>
      </v-tab-item>
    </v-tabs>

    <div class="version">JS-NG v{{ NGVersion }}, JS-SDK v{{ SDKVersion }}</div>

    <v-dialog v-if="dialog.expiration" v-model="dialog.expiration" width="400">
      <v-card
        v-if="vdc"
        :color="vdc.expiration_days < 2 ? 'error' : 'warning'"
        dark
      >
        <v-card-text>
          <v-row align="center" justify="center">
            <v-icon class="my-4" align="center" x-large justify="center" center
              >mdi-comment-alert-outline</v-icon
            >
          </v-row>
          <b class="font-weight-bold"
            >Your VDC will expire in <ins> {{ expirationTime }} </ins><br />
            You have a grace period of 14 days. Your workloads will be up but
            not accessible. To avoid workloads deletion, please fund the wallet
            with address: <ins> {{ wallet.address }} </ins> with
            {{ flavor }} plan's price of <ins> {{ price }} TFT </ins>. You can
            go to "Wallet Information" section in the left side to pay using
            QRCode.<br /><br />
            Please note: Funding the wallet with less than {{ price }} TFT will
            keep the workloads alive but will stay in grace period.
          </b>
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-dialog v-if="release" v-model="dialog.release" width="400">
      <v-card class="pt-4 pb-2" color="info" dark>
        <v-card-text>
          <v-row align="center" justify="center">
            <v-icon class="my-4" align="center" x-large justify="center" center
              >mdi-comment-alert-outline</v-icon
            >
          </v-row>
          <b class="font-weight-bold">
            New release {{ this.release }} is available. You can update it later
            from the user menu in the topbar.
          </b>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            class="text--lighten-2"
            color="grey"
            text
            @click="dialog.release = false"
          >
            Later
          </v-btn>
          <v-btn color="white" outlined @click="$emit('update-dashboard')">
            Update now
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
module.exports = {
  props: {
    alertid: {
      type: String,
      default: null,
    },
  },
  data() {
    return {
      tableloading: true,
      vdc: null,
      name: null,
      wallet: null,
      price: null,
      expirationData: null,
      flavor: null,
      expirationTime: null,
      raiseExpirationAlert: true,
      dialog: {
        expiration: false,
        release: false,
      },
      release: null,
      tabs: [
        { icon: "mdi-memory", title: "Compute Nodes" },
        { icon: "mdi-view-grid-plus-outline", title: "Virtual Machines" },
        { icon: "mdi-server", title: "Storage Containers" },
        { icon: "mdi-wallet", title: "Wallet Information" },
        { icon: "mdi-backup-restore", title: "Backup & Restore" },
        { icon: "mdi-alert-outline", title: "Alerts" },
        { icon: "mdi-account-lock", title: "Admins" },
        { icon: "mdi-shield-key", title: "API Keys" },
      ],
      activetab: 0,
      NGVersion: null,
      SDKVersion: null,
    };
  },
  methods: {
    vdcInfo() {
      this.tableloading = true;
      this.$api.vdc
        .getVdcInfo()
        .then((response) => {
          this.vdc = response.data;
          this.name = this.vdc.vdc_name;
          this.flavor = this.vdc.flavor;
        })
        .finally(() => {
          this.tableloading = false;
        });
      this.$api.vdc
        .getVdcPlanPrice()
        .then((response) => {
          this.price = response.data.price;
        })
        .catch((err) => {
          this.alert(err.message, "error");
        });
      this.$api.vdc
        .getVdcExpiration()
        .then((response) => {
          this.expirationData = response.data;
          this.expirationTime =
            this.expirationData.expiration_days > 1
              ? `${this.expirationData.expiration_days.toFixed(0)} days and ${(
                  (this.expirationData.expiration_days % 1) *
                  24
                ).toFixed(0)} hours,`
              : `${(this.expirationData.expiration_days * 24).toFixed(
                  0
                )} hours,`;
        })
        .catch((err) => {
          this.alert(err.message, "error");
        });
      this.$api.vdc
        .getVdcWalletInfo()
        .then((response) => {
          this.wallet = response.data;
        })
        .catch((err) => {
          this.alert(err.message, "error");
        });
    },

    checkDashboardUpdates() {
      this.$api.version.checkForUpdate().then((response) => {
        let new_release = response.data.new_release;
        if (new_release) {
          this.release = new_release;
          this.dialog.release = true;
        }
      });
    },
    getSDKVersion() {
      this.$api.version.getSDKVersion().then((response) => {
        const versions = response.data.data;
        this.NGVersion = versions["js-ng"];
        this.SDKVersion = versions["js-sdk"];
      });
    },
  },
  mounted() {
    this.getSDKVersion();
    this.vdcInfo();
    this.checkDashboardUpdates();
    if (this.alertid) {
      this.activetab = 4;
    }
  },
  updated() {
    if (this.raiseExpirationAlert && this.vdc) {
      if (this.vdc.expiration_days < 14) {
        this.dialog.expiration = true;
        this.raiseExpirationAlert = false;
        setTimeout(() => {
          this.raiseExpirationAlert = true;
        }, 60 * 60 * 1000); // Allow show alert after one hour
      }
    }
  },
};
</script>

<style scoped>
.v-tab {
  justify-content: left;
  text-align: left;
}
</style>
