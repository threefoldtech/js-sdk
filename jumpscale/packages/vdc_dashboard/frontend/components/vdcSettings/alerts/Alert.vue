<template>
  <base-dialog title="Alert details" v-model="dialog" :loading="loading">
    <template #default>
      <v-simple-table>
        <template v-slot:default>
        <tbody>
          <tr>
            <td>Id</td>
            <td>{{ alertdata.id }}</td>
          </tr>
          <tr>
            <td>Application</td>
            <td>{{ alertdata.appname }}</td>
          </tr>
          <tr>
            <td>Category</td>
            <td>{{ alertdata.category }}</td>
          </tr>
          <tr>
            <td>Message</td>
            <td><code>{{ alertdata.message }}</code></td>
          </tr>
        </tbody>
        </template>
      </v-simple-table>
      <code-area v-if="alertdata.tracebacks[0]" mode="python" :content="alertdata.tracebacks[0].raw"></code-area>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
    </template>
  </base-dialog>
</template>

<script>
  module.exports = {
    props: { alertdata: Object },
    mixins: [dialog]
  }
</script>
