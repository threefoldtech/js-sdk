<template>
  <div>
    <base-section title="Processes" icon="mdi-speedometer" :loading="loading">
      <template #actions>
        <v-text-field v-model="search" append-icon="mdi-magnify" label="Search" single-line hide-details solo flat></v-text-field>
      </template>
      <v-data-table :calculate-widths="true" :items-per-page="10" :headers="headers" :items="processes" :search="search" @click:row="open" :footer-props="{'disable-items-per-page': true}">
        <template slot="no-data">No processes available</p></template>
        <template v-slot:item.rss="{ item }">
          {{Math.round(item.rss)}} MB
        </template>
      </v-data-table>
    </base-section>

    <process-info v-model="dialog" :process="selected"></process-info>
  </div>
</template>

<script>
  module.exports = {
    components: {
      'process-info': httpVueLoader("./Process.vue")
    },
    data () {
      return {
        search: '',
        loading: false,
        selected: null,
        dialog: false,
        processes: [],
        headers: [
          {text: "Name", value: "name"},
          {text: "PID", value: "pid"},
          {text: "PPID", value: "ppid"},
          {text:"Status", value: "status"},
          {text: "User", value: "username"},
          {text: "Memory", value: "rss"}
        ]
      }
    },
    methods: {
      open (process) {
        this.selected = process
        this.dialog = true
      },
      getProcesses () {
        this.loading = true
        this.$api.health.getRunningProcesses().then((response) => {
          this.processes = JSON.parse(response.data).data
        }).finally (() => {
          this.loading = false
        })
      }
    },
    mounted () {
      this.getProcesses()
    }
  }
</script>

