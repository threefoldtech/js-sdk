<template>
  <v-container fluid class="grey lighten-5 mt-5">
    <v-row no-gutters>
      <v-col cols="6" md="2">
        <v-card width="256">
          <sidebar :name="name" :address="address" />
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="10">
        <router-view :vdc="vdc"></router-view>
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
  data() {
    return {
      loading: true,
      vdc: null,
      name: null,
      address: null,
    };
  },
  methods: {
    vdcInfo() {
      this.$api.solutions
        .getVdcInfo()
        .then((response) => {
          this.vdc = response.data;
          this.name = this.vdc.vdc_name;
          this.address = this.vdc.wallet_address;
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
