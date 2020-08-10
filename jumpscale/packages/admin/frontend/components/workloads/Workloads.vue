<template>
  <div>
    <base-component title="Workloads" icon="mdi-clipboard-list-outline" :loading="loading">
      <template #default>
        <v-data-table :headers="headers" :items="workloads" :footer-props="{'disable-items-per-page': true}" @click:row="open">
        </v-data-table>
      </template>
    </base-component>

    <workload-info v-model="dialog" :data="selected"></workload-info>
  </div>
</template>


<script>
  module.exports = {
    components: {
      'workload-info': httpVueLoader("./Workload.vue")
    },
    data () {
      return {
        loading: false,
        selected: null,
        dialog: false,
        workloads: [],
        headers: [
          {text: "ID", value: "id"},
          {text: "Workload Type", value: "workload_type"},
          {text: "Pool", value: "pool_id"},
          {text: "Next Action", value: "next_action"},
          {text: "Creation Time", value: "epoch"},
        ]
      }
    },
    methods: {
      getWorkloads () {
        this.loading = true
        this.$api.solutions.getAll().then((response) => {
          this.workloads = JSON.parse(response.data).data
        }).finally (() => {
          this.loading = false
        })
      },
      open (workload) {
        this.selected = workload
        this.dialog = true
      },
    },
    mounted () {
      this.getWorkloads()
    }
  }
</script>


<style scoped>
input {
  width: 50px;
}
.v-text-field {
  padding: 10px 0px !important;
}
</style>
