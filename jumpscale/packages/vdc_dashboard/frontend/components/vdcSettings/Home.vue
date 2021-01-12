<template>
  <v-container fluid class="grey lighten-5 mt-5">
    <v-tabs class="text--left" background-color="transparent" vertical>
      <v-tab>
        <v-icon left> mdi-memory </v-icon>
        Compute Nodes
      </v-tab>
      <v-tab>
        <v-icon left> mdi-server </v-icon>
        Storage Nodes
      </v-tab>
      <v-tab>
        <v-icon left> mdi-wallet </v-icon>
        Wallet Information
      </v-tab>

      <v-tab-item class="ml-2">
        <v-card flat>
          <kubernetes :vdc="vdc" :loading="loading"></kubernetes>
        </v-card>
      </v-tab-item>
      <v-tab-item class="ml-2">
        <v-card flat>
          <s3 :vdc="vdc"></s3>
        </v-card>
      </v-tab-item>
      <v-tab-item class="ml-2">
        <v-card flat>
          <wallet
            v-if="vdc"
            :wallet="wallet"
            :expirationdays="vdc.expiration_days"
            :expirationdate="vdc.expiration_date"
          ></wallet>
        </v-card>
      </v-tab-item>
    </v-tabs>
    <v-dialog v-model="dialog.expiration" width="400">
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
            Please fund the wallet with address: {{ wallet.address }}</b
          >
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
module.exports = {
  data() {
    return {
      loading: true,
      vdc: null,
      name: null,
      wallet: null,
      expirationTime: null,
      raiseExpirationAlert: true,
      dialog: {
        expiration: false,
      },
    };
  },
  methods: {
    vdcInfo() {
      this.loading = true;
      this.$api.solutions
        .getVdcInfo()
        .then((response) => {
          this.vdc = response.data;
          this.name = this.vdc.vdc_name;
          this.wallet = this.vdc.wallet;
          this.expirationTime =
            vdc.expiration_days > 1
              ? `${vdc.expiration_days.toFixed(0)} days and ${((vdc.expiration_days % 1) * 24).toFixed(0)} hours,`
              : `${(vdc.expiration_days * 24).toFixed(0)} hours,`;
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
  mounted() {
    this.vdcInfo();
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
