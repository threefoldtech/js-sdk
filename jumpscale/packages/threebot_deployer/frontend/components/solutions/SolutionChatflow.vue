<template>
  <external :url="url"></external>
</template>

<script>
  module.exports = {
    props: {topic: String},
    computed: {
      url () {
        return `/threebot_deployer/chats/${this.topic}?noheader=yes`
      }
    }
  }
</script>
