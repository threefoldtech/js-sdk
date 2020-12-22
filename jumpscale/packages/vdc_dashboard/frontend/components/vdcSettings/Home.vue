<template>
  <v-container fluid class="grey lighten-5 mt-5">
    <v-tabs vertical>
      <v-tab>
        <v-icon left> mdi-account </v-icon>
        Compute Nodes
      </v-tab>
      <v-tab>
        <v-icon left> mdi-lock </v-icon>
        Storage Nodes
      </v-tab>
      <v-tab>
        <v-icon left> mdi-access-point </v-icon>
        Wallet Information
      </v-tab>

      <v-tab-item>
        <v-card flat>
          <kubernetes :vdc="vdc"></kubernetes>
        </v-card>
      </v-tab-item>
      <v-tab-item>
        <v-card flat>
          <s3 :vdc="vdc"></s3>
        </v-card>
      </v-tab-item>
      <v-tab-item>
        <v-card flat>
          <wallet :wallet="wallet"></wallet>
        </v-card>
      </v-tab-item>
    </v-tabs>
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
    };
  },
  methods: {
    vdcInfo() {
      this.$api.solutions
        .getVdcInfo()
        .then((response) => {
          this.vdc = response.data;
          this.name = this.vdc.vdc_name;
          this.address = this.vdc.wallet;
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
  mounted() {
    this.vdcInfo();
  },
};
</script>
