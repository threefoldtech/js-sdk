<template>
  <external v-if="wikis[wiki]" :url="wikis[wiki].url"></external>
</template>

<script>
  module.exports = {
    props: {wiki: String},
    data () {
      return {
        wikis: WIKIS
      }
    }
  }
</script>
