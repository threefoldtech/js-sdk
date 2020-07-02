<template>
  <external :package="package" :name="name" :path="path" :url="url"></external>
</template>

<script>
  module.exports = {
    props: {topic: String},
    data () {
      return {
        package: true,
        name: "chatflows",
        path: "/sandbox/code/github/js-next/js-sdk/jumpscale/packages/chatflows"
      }
    },
    computed: {
      url () {
        return `/chatflows/tfgrid_solutions/chats/${this.topic}`
      }
    }
  }
</script>
