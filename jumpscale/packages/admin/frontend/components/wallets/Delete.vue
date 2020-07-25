<template>
  <base-dialog title="Delete wallet" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      Are you sure you want to delete wallet <strong>{{name}}</strong> ?
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
      this.$api.wallets.delete(this.name).then((response) => {
        this.done("Wallet is deleted")
      }).catch((error) => {
        this.error = error.response.data.error
      }).finally(() => {
        this.loading = false
      })
    }
  }
}
</script>
