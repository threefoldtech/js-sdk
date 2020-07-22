<template>
  <base-dialog title="Take Backup" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      <v-form>
        <v-text-field v-model="form.tags" label="Tages" dense></v-text-field>
      </v-form>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text @click="submit">Confirm</v-btn>
    </template>
  </base-dialog>  
</template>

<script>

module.exports = {
  mixins: [dialog],
  computed: {
    tags () {
      let tags = this.form.tags || ""
      return tags.trim().split(",")
    }
  },
  methods: {
    submit () {
      this.loading = true
      this.error = null
      this.$api.backup.take(this.tags).then((response) => {
        this.done("Backup is created")
      }).catch((error) => {
        this.error = error.message
      }).finally(() => {
        this.loading = false
      })
    }
  }
}
</script>
