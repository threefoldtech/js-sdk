<template>
  <base-dialog title="Add identity" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      <v-form>
        <v-text-field v-model="form.display_name" label="Display name" dense>
        <v-tooltip slot="append" left>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon v-bind="attrs" v-on="on">
                <v-icon color="grey lighten-1"> mdi-help-circle </v-icon>
              </v-btn>
            </template>
            <span>The name to be registered on TFGrid, used to reference your created 3Bot identity.</span>
        </v-tooltip>
        </v-text-field>
        <v-text-field v-model="form.email" label="Email" dense></v-text-field>
        <v-text-field v-model="form.words" label="Words" dense></v-text-field>
        <v-select v-model="selected_explorer" label="Explorer type" :items="Object.keys(explorers)" dense></v-select>
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
        selected_explorer: "Main Network",
      }
    },
    methods: {
        submit () {
            this.loading = true
            this.error = null
            if(!this.form.display_name || !this.form.email || !this.form.words || !this.selected_explorer){
                this.error = "All fields required"
                this.loading = false
            }
            else{
                this.$api.identities.add(this.form.display_name, this.form.email, this.form.words, this.explorers[this.selected_explorer].type).then((response) => {
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
