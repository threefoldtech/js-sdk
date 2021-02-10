<template>
  <base-section title="3Node Disk Usage" icon="mdi-database" :loading="loading">
    <v-row class="ma-0 pa-0">
      <v-col cols="6" class="ma-0 pa-0">
        <span>
          <v-icon small left color="primary">mdi-circle</v-icon> Used Space: {{usage.used}} GB
        </span><br>
         <span>
          <v-icon small left color="secondary">mdi-circle</v-icon> Available Space: {{usage.total - usage.used}} GB
        </span><br>
        <span>
          <v-icon small left>mdi-circle-outline</v-icon>
            Total Space: {{usage.total}} GB
        </span>
      </v-col>
      <v-col cols="6" class="ma-0 pa-0">
        <div class="text-center">
          <v-progress-circular :size="100" :rotate="-90" :width="10" :value="usage.percent" color="primary">
              {{Math.round(usage.percent)}}%
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
      getDiskUsage () {
        this.loading = true
        this.$api.health.getDiskUsage().then((response) => {
          this.usage = JSON.parse(response.data).data
        }).finally (() => {
          this.loading = false
        })
      },
    },
    mounted () {
      this.getDiskUsage()
    }
  }
</script>
