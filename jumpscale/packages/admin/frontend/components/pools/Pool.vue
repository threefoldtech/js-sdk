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
                <v-chip class="ma-1" v-for="(node_id, index) in pool.node_ids" :key="index" :to="`${pool.explorer_url}/nodes/${node_id}`">
                    {{ node_id }}
                </v-chip>
              </td>
            </tr>
            <tr>
              <td>Active Workloads</td>
              <td class="pt-2">
                <v-chip class="ma-1" v-for="(wid, index) in pool.active_workload_ids" :key="index" :to="`${pool.explorer_url}/reservations/workloads/${wid}`">
                  {{ wid }}
                </v-chip>
              </td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
    </template>
  </base-dialog>
</template>

<script>

module.exports = {
  props: {pool: Object},
  mixins: [dialog]
}
</script>
