<template>
  <div>
    <Message :payload="payload"></Message>
    <v-textarea v-model="val" :rules="rules" clearable clear-icon="mdi-close" validate-on-blur outlined></v-textarea>
  </div>
</template>

<script>  
  module.exports = {
    mixins: [field],
    props: {payload: Object}
  }
</script>
