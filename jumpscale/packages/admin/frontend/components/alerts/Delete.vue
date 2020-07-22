<template>
  <base-dialog title="Delete all alerts" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      Are you sure you want to delete all the alerts ?
    </template>
    <template #actions>
      <v-btn text @click="close">Cancel</v-btn>
      <v-btn text @click="submit">Yes</v-btn>
    </template>
  </base-dialog>  
</template>

<script>
  module.exports = {
    mixins: [dialog],
    methods: {
      submit () {
        this.loading = true
        this.error = null
        this.$api.alerts.deleteAll().then((response) => {
          this.done("alerts are deleted")
        }).catch((error) => {
          this.error = error.response.data.error
        }).finally(() => {
          this.loading = false
        })
      }
    }
  }
</script>