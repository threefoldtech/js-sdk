<template>
  <v-container fluid class="grey lighten-5 mt-5">
    <v-tabs class="text--left" background-color="transparent" vertical>
      <v-tab>
        <v-icon left> mdi-comment-processing-outline </v-icon>
        Compute Nodes
      </v-tab>
      <v-tab>
        <v-icon left> mdi-memory </v-icon>
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
      this.loading = true;
      this.$api.solutions
        .getVdcInfo()
        .then((response) => {
          this.vdc = response.data;
          this.name = this.vdc.vdc_name;
          this.wallet = this.vdc.wallet;
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

<style scoped>
.v-tab {
  justify-content: left;
  text-align: left;
}
</style>
