<template>
  <base-section title="Memory Usage" icon="mdi-memory" :loading="loading">
    <v-row class="ma-0 pa-0">
      <v-col cols="6" class="ma-0 pa-0">
        <span>
          <v-icon small left color="primary">mdi-circle</v-icon> Used Memory: {{usage.used}} GB
        </span><br>
        <span>
          <v-icon small left color="secondary">mdi-circle</v-icon> Available Memory: {{usage.total - usage.used}} GB
        </span><br>
        <span>
          <v-icon small left>mdi-circle-outline</v-icon> Total Memory: {{usage.total}} GB
        </span>
      </v-col>
      <v-col cols="6" class="ma-0 pa-0">
        <div class="text-center">
          <v-progress-circular :size="100" :rotate="-90" :width="10" :value="usage.percent" color="primary">
            {{Math.round((usage.used / usage.total) * 100)}}%
          </v-progress-circular>
        </div>
      </v-col>
    </v-row>
  </base-section>
</template>

<script>
  module.exports = {
    data () {
      return {
        search: '',
        loading: false,
        usage: {},
        headers: [
          {text: "Name", value: "name"},
          {text: "PID", value: "pid"},
          {text: "User", value: "username"},
          {text: "Memory", value: "rss"}
        ]
      }
    },
    methods: {
      getMemoryUsage () {
        this.loading = true
        this.$api.health.getMemoryUsage().then((response) => {
          this.usage = JSON.parse(response.data).data
        }).finally (() => {
          this.loading = false
        })
      },
    },
    mounted () {
      this.getMemoryUsage()
    }
  }
</script>
