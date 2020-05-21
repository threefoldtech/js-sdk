<template>
  <div>
    <Message :payload="payload"></Message>
    <v-text-field outlined v-model="val" :rules="rules" validate-on-blur type="number"></v-text-field>
  </div>
</template>

<script>  
  module.exports = {
    mixins: [field],
    props: {payload: Object}
  }
</script>
