<template>
  <div>
    <Message :payload="payload"></Message>
    <v-text-field v-model="val" :rules="rules" validate-on-change outlined></v-text-field>
  </div>
</template>

<script>
  module.exports = {
    mixins: [field],
    props: {payload: Object}
  }
</script>
