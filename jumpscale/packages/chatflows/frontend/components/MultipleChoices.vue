<template>
  <div>
    <Message :payload="payload"></Message>
    <v-checkbox v-model="val" v-for="(option, i) in payload.options" :rules="rules" :key="i" :label="option" :value="option"></v-checkbox>
  </div>
</template>

<script>
  module.exports = {
    mixins: [field],
    props: {payload: Object}
  }
</script>
