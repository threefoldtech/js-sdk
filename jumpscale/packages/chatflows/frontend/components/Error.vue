<template>
  <Message v-if="payload.kwargs.md || payload.kwargs.html" :payload="payload"></Message>
  <v-alert v-else outlined type="error">
    <strong>{{payload.msg}}</strong>
  </v-alert>
</template>

<script>
  module.exports = {
    props: {payload: Object}
  }
</script>
