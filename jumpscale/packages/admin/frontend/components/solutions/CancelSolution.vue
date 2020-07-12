<template>
  <base-dialog title="Cancel solution" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      Are you sure you want to cancel <strong>{{type}}</strong> <strong>{{name}}</strong>
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
  props: ["name", "type"],
  methods: {
    submit () {
      this.loading = true
      this.error = null
      this.$api.solutions.cancelReservation(this.type, this.name).then(response => {
        console.log("cancelled")
        this.$router.go(0);
      }).catch(err => {
        console.log("failed")
      });
    }
  }
}
</script>
