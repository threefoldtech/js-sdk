<template>
  <div>
    <Message :payload="payload"></Message>
    <div class="text-center">
      <img :src="src" style="border:1px dashed #85929E" width="250"/><br><br>
      <v-text-field v-model="val" outlined :rules="rules" validate-on-blur></v-text-field>
    </div>
  </div>
</template>

<script>  
  module.exports = {
    mixins: [field],
    props: {payload: Object},
    data () {
      return {
        validators: {
          required: true,
          is_valid: true
        },
      }
    },
    computed: {
      src () {
        return 'data:image/png;base64,' + this.payload.captcha
      }
    }
  }
</script>
