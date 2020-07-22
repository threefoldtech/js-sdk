<template>
  <base-dialog title="Remove admin" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      Are you sure you want to remove <strong>{{name}}</strong> from admins
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
  props: ["name"],
  methods: {
    submit () {
      this.loading = true
      this.error = null
      this.$api.admins.remove(this.name).then((response) => {
        this.done("Admin is removed")
      }).catch((error) => {
        this.error = error.response.data.error
      }).finally(() => {
        this.loading = false
      })
    }
  }
}
</script>
