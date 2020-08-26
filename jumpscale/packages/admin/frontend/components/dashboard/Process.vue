<template>
  <base-dialog title="Process details" v-model="dialog" :loading="loading">
    <template #default>
      <v-simple-table>
        <template v-slot:default>
          <tbody>
            <tr>
              <td>Name</td>
              <td>{{ process.name }}</td>
            </tr>
            <tr>
              <td>PID</td>
              <td>{{ process.pid }}</td>
            </tr>
            <tr>
              <td>User</td>
              <td>{{ process.username }}</td>
            </tr>
            <tr>
              <td>Memory</td>
              <td>{{ process.rss }} MB</td>
            </tr>
            <tr>
              <td>Ports</td>
              <td class="pt-2">
                <v-chip class="ma-1" v-for="(port, index) in process.ports" :key="index">
                  {{ port.port }} ({{ port.status }})
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
  props: {process: Object},
  mixins: [dialog]
}
</script>
