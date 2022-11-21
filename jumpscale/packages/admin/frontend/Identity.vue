<template>
  <base-dialog title="Configure your identity" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      <v-form>
        <v-combobox label="Label" v-model="form.label" :items="Object.keys(identities)" @change="changeIdentity">
        </v-combobox>
        <v-text-field v-model="form.tname" label="3Bot name" dense></v-text-field>
        <v-text-field v-model="form.email" label="Email" dense></v-text-field>
        <v-text-field type="password" v-model="form.words" label="Secret words" dense></v-text-field>
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
  data() {
    return {
      identities: [],
    }
  },
  watch: {
    dialog(val) {
      if (val) this.getIdentities()
    }
  },
  methods: {
    changeIdentity() {
      if (this.form.label in this.identities) {
        this.form.tname = this.identities[this.form.label].name
        this.form.email = this.identities[this.form.label].email
      } else {
        this.form.tname = null
        this.form.email = null
      }
    },
    getIdentities() {
      this.$api.identity.list().then((response) => {
        this.identities = JSON.parse(response.data)
      })
    },
    submit() {
      this.loading = true
      this.error = null
      this.$api.identity.set(this.form.label, this.form.tname, this.form.email, this.form.words).then((response) => {
        this.done("Identity is updated")
        location.reload()
      }).catch((error) => {
        this.error = error.message
      }).finally(() => {
        this.loading = false
      })
    }
  }
}
</script>
