<template>
  <base-dialog title="Hide pool" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      Are you sure you want to hide this pool?
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text color="error" @click="submit">Confirm</v-btn>
    </template>
  </base-dialog>
</template>

<script>

module.exports = {
  mixins: [dialog],
  props: ["pool_id"],
  methods: {
    submit () {
      this.loading = true
      this.error = null
      this.$api.solutions.hidePool(this.pool_id).then(response => {
        console.log("Hided")
        window.location.reload();
      }).catch(err => {
        console.log("failed")
      });
    }
  }
}
</script>
