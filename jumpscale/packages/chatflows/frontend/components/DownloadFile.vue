<template>
  <div>
    <Message :payload="payload"></Message>
    <v-btn x-large color="success" width="300" height="50" @click="download">
      <v-icon left x-larg>mdi-download</v-icon> Download
    </v-btn>
  </div>
</template>

<script>  
  module.exports = {
    mixins: [field],
    props: {payload: Object},
    methods: {
      download () {
        const blob = new Blob([this.payload.data])
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', this.payload.filename)
        document.body.appendChild(link)
        link.click()
        link.parentNode.removeChild(link)
      }
    }
  }
</script>
