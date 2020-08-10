<template>
  <base-dialog title="Pool details" v-model="dialog" :loading="loading">
    <template #default>
      <v-simple-table>
        <template v-slot:default>
          <tbody>
            <tr>
              <td>ID</td>
              <td>{{ pool.pool_id }}</td>
            </tr>
            <tr>
              <td>Name</td>
              <td>
                <div class="justify-center">
                  <v-row>
                    <div style="margin-top: 15px;">{{ pool.name }}</div>
                    <v-spacer></v-spacer>
                    <v-text-field
                      v-if="edting"
                      v-model="name"
                      label="New name"
                      hint
                      persistent-hint
                    ></v-text-field>
                    <v-btn v-if="!edting" small color="warning" @click="startEdit()" dark>Edit</v-btn>
                    <div style="margin-top: 20px; margin-left: 10px;">
                      <v-btn v-if="edting" small color="error" @click="cancelEdit()" dark>close</v-btn>
                      <v-btn
                        v-if="edting"
                        small
                        color="success"
                        @click="rename(pool.pool_id, name)"
                        dark
                      >save</v-btn>
                    </div>
                  </v-row>
                </div>
              </td>
            </tr>
            <tr>
              <td>Farm</td>
              <td>{{ pool.farm }}</td>
            </tr>
            <tr>
              <td>Expiration</td>
              <td>{{ pool.empty_at }}</td>
            </tr>
            <tr>
              <td>Compute Units</td>
              <td>{{ pool.cus }}</td>
            </tr>
            <tr>
              <td>Storage Units</td>
              <td>{{ pool.sus }}</td>
            </tr>
            <tr>
              <td>Active Compute Units</td>
              <td>{{ pool.active_cu }}</td>
            </tr>
            <tr>
              <td>Active Storage Units</td>
              <td>{{ pool.active_su }}</td>
            </tr>
            <tr>
              <td>Nodes</td>
              <td class="pt-2">
                <v-chip class="ma-1" v-for="(node_id, index) in pool.node_ids" :key="index">
                  <a :href="`${pool.explorer_url}/nodes/${node_id}`">{{ node_id }}</a>
                </v-chip>
              </td>
            </tr>
            <tr>
              <td>Active Workloads</td>
              <td class="pt-2">
                <v-chip
                  class="ma-1"
                  v-for="(wid, index) in pool.active_workload_ids"
                  :key="index"
                >{{ wid }}</v-chip>
              </td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </template>
    <template #actions>
      <v-btn text color="error" @click="hide(pool.pool_id)">Hide</v-btn>
      <v-btn text @click="close">Close</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  data() {
    return {
      edting: false,
      name: "",
    };
  },
  props: { pool: Object },
  mixins: [dialog],
  methods: {
    startEdit() {
      console.log(this.edting);
      this.edting = true;
    },
    cancelEdit() {
      this.name = "";
      this.edting = false;
    },
    rename(pool_id, name) {
      this.$api.solutions.renamePool(pool_id, name);
      window.location.reload();
    },
    hide(pool_id) {
      this.$api.solutions.hidePool(pool_id);
      window.location.reload();
    },
  },
};
</script>
