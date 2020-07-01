<template>
  <external v-if="explorer" :url="`https://${explorer.url}`"></external>
</template>

<script>
module.exports = {
  data () {
    return {
      explorer: null,
      loading: false
    }
  },
  methods: {
    getCurrentExplorer () {
      this.loading = true
      this.$api.explorers.get().then((response) => {
        this.explorer = JSON.parse(response.data).data
      }).finally(() => {
        this.loading = false
      })
    }
  },
  mounted () {
    this.getCurrentExplorer()
  }
}
</script>
