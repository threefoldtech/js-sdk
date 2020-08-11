<template>
  <base-dialog title="Patch Cancel Workloads" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      Are you sure you want to cancel all {{ wids.length }} selected workloads?
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
      this.$api.solutions.patchCancelWorkload(this.wids).then(response => {
        this.$router.go(0);
      }).catch(err => {
        console.log("failed")
        this.loading = false
        this.error = err
      });
    },
    cancel () {
        this.dialogs.patchCancelWorkloads = false;
      },
  }
}
</script>
