<template>
  <base-dialog title="Delete application logs" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      Are you sure you want to delete all the logs of application <strong>{{appname}}</strong> ?
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
    props: ["appname"],
    methods: {
      submit () {
        this.loading = true
        this.error = null
        this.$api.logs.delete(this.appname).then((response) => {
          this.done("logs are deleted")
        }).catch((error) => {
          this.error = error.response.data.error
        }).finally(() => {
          this.loading = false
        })
      }
    }
  }
</script>