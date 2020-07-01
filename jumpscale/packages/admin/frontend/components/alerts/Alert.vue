<template>
  <base-dialog title="Alert details" v-model="dialog" :loading="loading">
    <template #default>
      <v-simple-table>
        <template v-slot:default>
        <tbody>
          <tr>
            <td>Id</td>
            <td>{{ alert.id }}</td>
          </tr>
          <tr>
            <td>Application</td>
            <td>{{ alert.appname }}</td>
          </tr>
          <tr>
            <td>Category</td>
            <td>{{ alert.category }}</td>
          </tr>
          <tr>
            <td>Message</td>
            <td><code>{{ alert.message }}</code></td>
          </tr>
        </tbody>
        </template>
      </v-simple-table>
      <code-area mode="python" :content="alert.tracebacks[0].raw"></code-area>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
    </template>
  </base-dialog>  
</template>

<script>
  module.exports = {
    props: {alert: Object},
    mixins: [dialog]
  }
</script>

