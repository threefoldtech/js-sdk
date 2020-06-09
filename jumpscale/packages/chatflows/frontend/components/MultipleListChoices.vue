<template>
  <div>
    <Message :payload="payload"></Message>
    <v-autocomplete v-if="payload.kwargs.auto_complete" v-model="val" :items="payload.options" :rules="rules" validate-on-blur outlined multiple small-chips></v-autocomplete>
    <v-select v-else v-model="val" :items="payload.options" :rules="rules" validate-on-blur small-chips multiple outlined/>
  </div>
</template>

<script>
  module.exports = {
    mixins: [field],
    props: {payload: Object}
  }
</script>
