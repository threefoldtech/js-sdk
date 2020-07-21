<template>
  <external :package="package" :name="name" :giturl="giturl" :url="url"></external>
</template>

<script>
  module.exports = {
    data () {
      return {
        package: true,
        name: "notebooks",
        giturl: "https://github.com/threefoldtech/js-sdk/blob/development_notebooks_package/jumpscale/packages/notebooks",
        url: "/notebooks/"
      }
    }
  }
</script>
