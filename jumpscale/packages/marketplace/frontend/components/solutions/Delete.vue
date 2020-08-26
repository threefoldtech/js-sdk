<template>
  <base-dialog title="Cancel workload" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      Are you sure you want to cancel?
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
  props: ["wids"],
  methods: {
    submit () {
      this.loading = true
      this.error = null
      this.$api.solutions.cancelReservation(this.wids).then(response => {
        console.log("cancelled")
        this.$router.go(0);
      }).catch(err => {
        console.log("failed")
      });
    }
  }
}
</script>
