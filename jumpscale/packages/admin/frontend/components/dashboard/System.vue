<template>
  <base-section title="System Info" icon="mdi-information-outline" :loading="loading">
    <span>
      <v-icon left color="primary">mdi-code-tags-check</v-icon> Software version: 0.2
    </span><br>
    <span>
      <v-icon left color="primary">mdi-ip-network</v-icon> IP Address: 172.17.0.2
    </span><br>
  </base-section>
</template>

<script>
  module.exports = {
    data () {
      return {
        loading: false
      }
    }
  }
</script>
