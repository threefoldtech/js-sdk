<template>
  <div>
    <Message :payload="payload"></Message>
    <v-file-input @change="readFile" prepend-icon="mdi-paperclip" label="File input" show-size :rules="rules" validate-on-blur outlined></v-file-input>
    <v-sheet v-if="val" color="accent" class="pa-5">
      <pre>{{val}}</pre>
    </v-sheet><br><br>
  </div>
</template>

<script>
  module.exports = {
    mixins: [field],
    props: {payload: Object},
    data () {
      return {
        file: null,
        validators: {}
      }
    },
    methods: {
      readFile (file) {
        this.file = file
        const reader = new FileReader()
        reader.onload = (event) => {
          this.val = event.target.result
        }
        if (file) {
          reader.readAsText(file)
        }
      }
    }
  }
</script>

<style scoped>
  pre {
    word-wrap: break-word;
    white-space: pre-wrap;
  }
</style>
