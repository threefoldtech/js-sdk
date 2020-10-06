<template>
  <div>
    <base-component title="Workloads" icon="mdi-clipboard-list-outline">
      <template #actions>
        <v-btn color="primary" :disabled="!delete_enabled" @click="cancelSelected">
          <v-icon left>mdi-delete</v-icon>Delete Selected
        </v-btn>
      </template>
      <template #default>
        <v-data-table
          v-model="selected_rows"
          show-select
          :headers="headers"
          :items="data.reverse()"
          @click:row="open"
          :page.sync="page"
          :loading="loading"
        >
          <template slot="no-data">No workloads available</p></template>
          <template v-slot:item.epoch="{ item }">{{ new Date(item.epoch * 1000).toLocaleString('en-GB') }}</template>
          <template v-slot:body.prepend="{ headers }">
            <tr>
              <td></td>
              <td>
                <v-text-field v-model="filters.id" clearable filled hide-details dense></v-text-field>
              </td>
              <td>
                <v-select
                  v-model="filters.workload_type"
                  :items="types"
                  clearable
                  filled
                  hide-details
                  dense
                ></v-select>
              </td>
              <td>
                <v-select
                  v-model="filters.pool_id"
                  :items="pools"
                  clearable
                  filled
                  hide-details
                  dense
                ></v-select>
              </td>
              <td>
                <v-select
                  v-model="filters.next_action"
                  :items="actions"
                  clearable
                  filled
                  hide-details
                  dense
                ></v-select>
              </td>
            </tr>
          </template>
        </v-data-table>
      </template>
    </base-component>

    <workload-info v-model="dialogs.dialog" v-if="selected" :workload="selected"></workload-info>
    <patch-cancel v-model="dialogs.patchCancelWorkloads" :selected="todelete"></patch-cancel>
  </div>
</template>


<script>
module.exports = {
  components: {
    "workload-info": httpVueLoader("./Workload.vue"),
    "patch-cancel": httpVueLoader("./PatchCancel.vue"),
  },
  data() {
    return {
      loading: true,
      selected: null,
      selected_rows: [],
      workloads: [],
      types: [],
      pools: [],
      actions: [],
      page: 1,
      filters: {
        id: null,
        pool_id: null,
        workload_type: null,
        next_action: null,
      },
      headers: [
        { text: "ID", value: "id" },
        { text: "Workload Type", value: "workload_type" },
        { text: "Pool", value: "pool_id" },
        { text: "Next Action", value: "next_action" },
        { text: "Creation Time", value: "epoch" },
      ],
      dialogs: {
        dialog: false,
        patchCancelWorkloads: false,
      },
    };
  },
  computed: {
    data() {
      return this.workloads.filter((record) => {
        let result = [];
        Object.keys(this.filters).forEach((key) => {
          result.push(
            !this.filters[key] ||
              String(record[key]).includes(this.filters[key])
          );
        });
        return result.every(Boolean);
      });
    },
    delete_enabled() {
      return this.selected_rows.length > 0;
    },
    todelete() {
      let res = [];
      for (i = 0; i < this.selected_rows.length; i++) {
        res.push(this.selected_rows[i]);
      }
      return res;
    },
  },
  methods: {
    getWorkloads() {
      this.loading = true;
      this.pools = [];
      this.types = [];
      this.actions = [];
      this.$api.solutions
        .getAll()
        .then((response) => {
          this.workloads = JSON.parse(response.data).data;
          for (let i = 0; i < this.workloads.length; i++) {
            let workload = this.workloads[i];
            if (!this.pools.includes(workload.pool_id)) {
              this.pools.push(workload.pool_id);
            }
            if (!this.actions.includes(workload.next_action)) {
              this.actions.push(workload.next_action);
            }
            if (!this.types.includes(workload.workload_type)) {
              this.types.push(workload.workload_type);
            }
            // show node id
            workload["node id"] = workload.info.node_id;
            // show workload state
            workload.state = Workload_STATE[workload.info.result.state];
            workload.message = workload.info.result.message;
            // convert vloume type
            if (workload.workload_type === "Volume")
              workload.type = VOLUMES_TYPE[workload.type];
            // convert container disk type
            if (workload.workload_type === "Container") {
              workload.capacity.disk_type =
                VOLUMES_TYPE[workload.capacity.disk_type];
              workload.network_connection = workload.network_connection[0];
            }
          }
        })
        .finally(() => {
          this.loading = false;
        });
    },
    open(workload) {
      this.selected = workload;
      this.dialogs.dialog = true;
    },
    cancelSelected() {
      this.dialogs.patchCancelWorkloads = true;
    },
  },
  mounted() {
    this.getWorkloads();
  },
};
</script>


<style scoped>
input {
  width: 50px;
}
.v-text-field {
  padding: 10px 0px !important;
}
.v-data-table tr {
  cursor: pointer;
}
</style>
