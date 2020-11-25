<template>
  <v-container fluid class="grey lighten-5 mt-5">
    <v-row no-gutters>
      <v-col cols="6" md="2">
        <v-card width="256">
          <sidebar :name="name" />
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
  props: ["name"],
  data() {
    return {
      loading: true,
      vdc: null,
    };
  },
  methods: {
    vdcInfo() {
      this.$api.solutions
        .getVdcInfo(this.name)
        .then((response) => {
          this.vdc = response.data;
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
