<template>
  <base-dialog title="Add New Package" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      <v-form>
        <v-text-field v-model="form.path" label="Path" dense></v-text-field>
        <v-text-field v-model="form.giturl" label="Git url" dense></v-text-field>
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
      this.$api.packages.add(this.form.path, this.form.giturl).then((response) => {
        this.done("Package is added")
      }).catch((error) => {
        this.error = error.message
      }).finally(() => {
        this.loading = false
      })
    }
  }
}
</script>
