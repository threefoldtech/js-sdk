<template>
  <base-dialog title="Log details" v-model="dialog" :loading="loading">
    <template #default>
      <v-simple-table>
        <template v-slot:default>
        <tbody>
          <tr>
            <td>Id</td>
            <td>{{ record.id }}</td>
          </tr>
          <tr>
            <td>Application</td>
            <td>{{ record.appname }}</td>
          </tr>
          <tr>
            <td>Category</td>
            <td>{{ record.category }}</td>
          </tr>
          <tr>
            <td>Process Id</td>
            <td>{{ record.processid }}</td>
          </tr>
          <tr>
            <td>Context</td>
            <td>{{ record.context }}</td>
          </tr>
          <tr>
            <td>File</td>
            <td>{{ record.file.path }}</td>
          </tr>
          <tr>
            <td>Message</td>
            <td><code>{{ record.message }}</code></td>
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
  props: {record: Object},
  mixins: [dialog]
}
</script>

