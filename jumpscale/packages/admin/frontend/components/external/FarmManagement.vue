<template>
  <external :package="package" :name="name" :giturl="giturl" :url="url"></external>
</template>

<script>
  module.exports = {
    data () {
      return {
        package: true,
        name: "farmmanagement",
        giturl: "https://github.com/threefoldtech/js-sdk/blob/development/jumpscale/packages/farmmanagement",
        url: "/farmmanagement/"
      }
    }
  }
</script>
