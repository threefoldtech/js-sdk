<template>
  <base-dialog title="Delete package" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      Are you sure you want to delete package <strong>{{name}}</strong> ?
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text @click="submit">Submit</v-btn>
    </template>
  </base-dialog>  
</template>

<script>

module.exports = {
  mixins: [dialog],
  props: ["name"],
  methods: {
    submit () {
      this.loading = true
      this.error = null
      this.$api.packages.delete(this.name).then((response) => {
        this.done("Package is deleted")
      }).catch((error) => {
        this.error = error.response.data.error
      }).finally(() => {
        this.loading = false
      })
    }
  }
}
</script>
