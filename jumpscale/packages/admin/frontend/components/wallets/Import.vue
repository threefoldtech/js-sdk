<template>
  <base-dialog title="Import wallet" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      <v-form>
        <v-text-field v-model="form.name" label="Name" dense></v-text-field>
        <v-text-field v-model="form.secret" label="Secret" dense></v-text-field>
        <v-text-field v-model="form.network" label="Network" dense></v-text-field>
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
      this.$api.wallets.import(this.form.name, this.form.secret, this.form.network).then((response) => {
        this.done("Wallet is imported")
      }).catch((error) => {
        this.error = error.message
      }).finally(() => {
        this.loading = false
      })
    }
  }
}
</script>
