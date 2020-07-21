<template>
  <div>
    <Message :payload="payload"></Message>
    <v-simple-table>
      <template v-slot:default>
        <thead>
          <tr>
            <th class="text-left">Name</th>
            <th class="text-left">Value</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(value, name) in payload.data" :key="name">
            <td><strong>{{ name }}</strong></td>
            <td>{{ value }}</td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </div>
</template>

<script>
  module.exports = {
    props: {payload: Object}
  }
</script>
