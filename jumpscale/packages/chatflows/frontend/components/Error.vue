<template>
  <Message v-if="payload.kwargs.md || payload.kwargs.html" :payload="payload"></Message>
  <v-alert v-else outlined type="error">
    <strong v-if="payload.kwargs.htmlAlert" v-html="payload.msg">{{payload.msg}}</strong>
    <strong v-else>{{payload.msg}}</strong>
  </v-alert>
</template>

<script>
  module.exports = {
    props: {payload: Object},
  }
</script>
