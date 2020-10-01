<template>
  <base-section title="Health Checks" icon="mdi-pulse" :loading="loading">
    <v-chip
      v-for="service in services"
      :key="service.name"
      class="mr-2 mb-2"
      :color="service.status?'green':'red'"
    >
      <v-icon
        medium
        left
        color="white"
      >{{service.status?"mdi-checkbox-marked-circle":"mdi-close-circle"}}</v-icon>
      <div class="chip-txt">{{service.name}}</div>
    </v-chip>
  </base-section>
</template>

<script>
module.exports = {
  data() {
    return {
      loading: false,
      services: {}
    };
  },
  methods: {
    getHealthChecks() {
      this.loading = true;
      this.$api.health
        .getHealthChecks()
        .then(response => {
          this.services = JSON.parse(response.data).data;
        })
        .finally(() => {
          this.loading = false;
        });
    }
  },
  mounted() {
    this.getHealthChecks();
  }
};
</script>

<style scoped>
.chip-txt {
  color: white;
}

.green {
  background-color: #5caa5f !important;
}
</style>
