<template>
  <div>
    <Message :payload="payload"></Message>
    <v-text-field v-model="val" :rules="rules" :append-icon="icon" :type="type" @click:append="show = !show" validate-on-blur outlined></v-text-field>
  </div>
</template>

<script>  
  module.exports = {
    mixins: [field],
    props: {payload: Object},
    data () {
      return {
        show: false,
        icon: "mdi-eye-off",
        type: "password"
      }
    },
    watch: {
      show (value) {
        this.type = value ? "text" : "password"
        this.icon = value ? "mdi-eye" : "mdi-eye-off"
      }
    }
  }
</script>
