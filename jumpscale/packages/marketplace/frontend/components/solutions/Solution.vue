<template>
  <external :url="url"></external>
</template>

<script>
  module.exports = {
    props: {topic: String},
    computed: {
      url () {
        return `/marketplace/chats/${this.topic}`
      }
    }
  }
</script>
