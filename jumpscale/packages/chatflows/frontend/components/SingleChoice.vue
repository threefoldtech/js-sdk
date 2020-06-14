<template>
  <div>
    <Message :payload="payload"></Message>
    <v-radio-group v-model="val" :rules="rules" validate-on-blur column>
      <v-radio v-for="(option, i) in payload.options" :key="i" :label="option" :color="getColor(i)" :value="option"></v-radio>
    </v-radio-group>
  </div>
</template>

<script>
  module.exports = {
    mixins: [field],
    props: {payload: Object},
    data () {
        return {
          selected: null,
          colors: [
            "#5DADE2",
            "#E74C3C",
            "#52BE80",
            "#F5B041",
            "#AF7AC5",
          ]
        }
    },
    methods: {
      getColor (i) {
        if (i > this.colors.length - 1) {
          return this.colors[i % this.colors.length]
        } else {
          return this.colors[i]
        }
      }
    }
  }
</script>

<style  scoped>
  .v-radio {
    border: 1px solid #ECF0F1;
    border-radius: 10px !important;
    margin: 15px 0px;
    padding:15px;
  }
</style>
