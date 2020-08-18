<template>
  <base-section title="Health Checks" icon="mdi-pulse" :loading="loading">
    <div v-if="health_checks.stellar">
      <v-chip class="mr-2 mb-2" color="green">
        <v-icon medium left color="white">mdi-checkbox-marked-circle</v-icon>
        <div class="chip-txt">Stellar</div>
      </v-chip>
    </div>
    <div v-else>
    <v-chip class="mr-2 mb-2" color="red">
      <v-icon medium left color="white">mdi-close-circle</v-icon>
      <div class="chip-txt">Stellar</div>
    </v-chip>
    </div>
  </base-section>
</template>

<script>
  module.exports = {
    data () {
      return {
        loading: false,
        health_checks: {  // default true = all is working
          stellar: true,
        },
      }
    },
    methods: {
      getHealthChecks () {
        this.loading = true
        this.$api.health.getHealthChecks().then((response) => {
          this.health_checks = JSON.parse(response.data).data
        }).finally (() => {
          this.loading = false
        })
      },
    },
    mounted () {
      this.getHealthChecks()
    }
  }
</script>

<style scoped>
.chip-txt {
  color:white
}
</style>
