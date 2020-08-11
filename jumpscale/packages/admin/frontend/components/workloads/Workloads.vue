<template>
  <div>
    <base-component title="Workloads" icon="mdi-clipboard-list-outline" :loading="loading">
      <template #actions>
        <v-btn color="primary" :disabled="!delete_enabled" @click="cancelSelected">
          <v-icon left>mdi-delete</v-icon> Delete Selected
        </v-btn>
      </template>
      <template #default>
        <v-data-table v-model="selected_rows" show-select :headers="headers" :items="data" :footer-props="{'disable-items-per-page': true}" @click:row="open">
            <template v-slot:item.epoch="{ item }">
            {{ new Date(item.epoch * 1000).toLocaleString() }}
          </template>
          <template v-slot:body.prepend="{ headers }">
          <tr>
              <td>
              </td>
              <td>
                <v-text-field v-model="filters.id" clearable filled hide-details dense></v-text-field>
              </td>
              <td>
              <v-select v-model="filters.workload_type" :items="types" clearable filled hide-details dense></v-select>
              </td>
              <td>
              <v-select v-model="filters.pool_id" :items="pools" clearable filled hide-details dense></v-select>
              </td>
              <td>
              <v-select v-model="filters.next_action" :items="actions" clearable filled hide-details dense></v-select>
              </td>
          </tr>
          </template>
        </v-data-table>
      </template>
    </base-component>

    <workload-info v-model="dialog" :data="selected"></workload-info>
  </div>
</template>


<script>
  module.exports = {
    components: {
      'workload-info': httpVueLoader("./Workload.vue"),
      'patch-cancel': httpVueLoader("./PatchCancel.vue")
    },
    data () {
      return {
        loading: false,
        selected: null,
        selected_rows: [],
        dialog: false,
        workloads: [],
        types: [],
        pools: [],
        actions: [],
        filters: {
          id: null,
          pool_id: null,
          workload_type: null,
          next_action: null,
        },
        headers: [
          {text: "ID", value: "id"},
          {text: "Workload Type", value: "workload_type"},
          {text: "Pool", value: "pool_id"},
          {text: "Next Action", value: "next_action"},
          {text: "Creation Time", value: "epoch"},
        ],
        dialogs: {
          patchCancelWorkloads: false,
        },
      }
    },
    computed: {
      data () {
        return this.workloads.filter((record) => {
          let result = []
          Object.keys(this.filters).forEach(key => {
            result.push(!this.filters[key] || String(record[key]).includes(this.filters[key]))
          })
          return result.every(Boolean)
        })
      },
      delete_enabled() {
        if (this.selected_rows.length > 0) {
          return true
        }
        return false
      }
    },
    methods: {
      getWorkloads () {
        this.loading = true
        this.pools = []
        this.types = []
        this.actions = []
        this.$api.solutions.getAll().then((response) => {
          this.workloads = JSON.parse(response.data).data
          for (let i = 0; i < this.workloads.length; i++) {
            let workload = this.workloads[i];
            if (!this.pools.includes(workload.pool_id)) {
                this.pools.push(workload.pool_id)
            }
            if (!this.actions.includes(workload.next_action)) {
                this.actions.push(workload.next_action)
            }
            if (!this.types.includes(workload.workload_type)) {
                this.types.push(workload.workload_type)
            }
          }
        }).finally (() => {
          this.loading = false
        })
      },
      open (workload) {
        this.selected = workload
        this.dialog = true
      },
      cancelSelected() {
        console.log(this.selected_rows)
        // TODO: patch show external component for confirmation
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
