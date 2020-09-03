<template>
  <base-dialog title="Add identity" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      <v-form>
        <v-text-field v-model="form.instance_name" label="Identity name" dense></v-text-field>
        <v-text-field v-model="form.tname" label="3Bot name" dense></v-text-field>
        <v-text-field v-model="form.email" label="Email" dense></v-text-field>
        <v-text-field v-model="form.words" label="Words" dense></v-text-field>
        <v-select v-model="form.explorer_type" label="Explorer type" :items="explorer_labels" dense></v-select>
      </v-form>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text @click="submit">Add</v-btn>
    </template>
  </base-dialog>
</template>

<script>

module.exports = {
  mixins: [dialog],
    data () {
      return {
        explorers: {
          "Main Network": {url: "https://explorer.grid.tf", type: "main"},
          "Test Network": {url: "https://explorer.testnet.grid.tf", type: "testnet"}
        },
        explorer_labels:["Main Network","Test Network"]
      }
    },
    methods: {
        submit () {
            this.loading = true
            this.error = null
            if(!this.form.instance_name || !this.form.tname || !this.form.email || !this.form.words || !this.form.explorer_type){
                this.error = "All fields required"
                this.loading = false
            }
            else{
                this.$api.identities.add(this.form.instance_name, this.form.tname, this.form.email, this.form.words, this.explorers[this.form.explorer_type].type).then((response) => {
                    responseMessage = JSON.parse(response.data).data
                    if(responseMessage == "Identity with the same instance name already exists"){
                        this.error = responseMessage
                    }
                    else{
                        this.done("New Identity added", "success")
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
