<template>
  <external :package="package" :name="name" :path="path" :url="url"></external>
</template>

<script>
  module.exports = {
    data () {
      return {
        package: true,
        name: "farmmanagement",
        path: "/sandbox/code/github/js-next/js-sdk/jumpscale/packages/farmmanagement",
        url: "/farmmanagement/"
      }
    }
  }
</script>
