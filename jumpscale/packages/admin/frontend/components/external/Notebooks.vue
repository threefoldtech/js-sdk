<template>
  <external :package="package" :name="name" :giturl="giturl" :url="url"></external>
</template>

<script>
  module.exports = {
    data () {
      return {
        package: true,
        name: "notebooks",
        url: "/notebooks/"
      }
    }
  }
</script>
