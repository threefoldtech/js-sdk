<template>
  <base-dialog title="Delete solution" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      Are you sure you want to delete this solution ?
    </template>
    <template #actions>
      <v-btn text @click="close">Cancel</v-btn>
      <v-btn text @click="submit">Yes</v-btn>
    </template>
  </base-dialog>
</template>

<script>
  module.exports = {
    mixins: [dialog],
    props: { data: Object },
    methods: {
      submit() {
        this.loading = true
        this.error = null
        this.$api.solutions
          .cancelReservation(this.data.solution_type, this.data.id)
          .then(response => {
            this.$router.go(0);
          })
          .catch(err => {
            this.error = err.response.data.message
          })
          .finally (() => {
            this.loading = false
          })
      }
    }
  }
</script>
