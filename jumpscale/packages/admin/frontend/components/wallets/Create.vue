<template>
  <base-dialog title="Create new wallet" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      <v-form @submit="submit">
        <v-text-field v-model="form.name" label="Wallet name" dense></v-text-field>
      </v-form>
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
  methods: {
    submit () {
      this.loading = true
      this.error = null
      this.$api.wallets.create(this.form.name).then((response) => {
        this.done("Wallet is created")
      }).catch((error) => {
        this.error = error.response.data.error
      }).finally(() => {
        this.loading = false
      })
    }
  }
}
</script>
