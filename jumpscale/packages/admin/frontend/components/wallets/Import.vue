<template>
  <base-dialog title="Import wallet" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      <v-form>
        <v-text-field v-model="form.name" label="Name" dense></v-text-field>
        <v-text-field v-model="form.secret" label="Secret" dense></v-text-field>
        <v-select v-model="form.network" label="Network" :items="wallet_networks" dense></v-select>
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
  data () {
    return {
      wallet_networks:["STD","TEST"]
    }
  },
  methods: {
    submit () {
      this.loading = true
      this.error = null
      if(!this.form.name || !this.form.secret || !this.form.network){
          this.error = "All fields required"
          this.loading = false
      }
      else{
        this.$api.wallets.import(this.form.name, this.form.secret, this.form.network).then((response) => {
          response_data = JSON.parse(response.data)
          if("error" in response_data){
            this.error = response_data.error
          }
          else{
            this.done("Wallet is imported")
          }
        }).catch((error) => {
          this.error = error.response.data.error
        }).finally(() => {
          this.loading = false
        })
      }
    }
  }
}
</script>
