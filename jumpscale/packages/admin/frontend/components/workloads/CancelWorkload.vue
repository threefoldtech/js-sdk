<template>
  <base-dialog
    title="Cancel Workload"
    v-model="dialog"
    :error="error"
    :info="info"
    :loading="loading"
  >
    <template #default>Are you sure you want to cancel workload {{ workload.id }}?</template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text color="error" @click="submit">Confirm</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  mixins: [dialog],
  props: ["workload"],
  methods: {
    submit() {
      this.loading = true;
      this.error = null;
      this.info = null;

      this.$api.solutions
        .cancelWorkload(this.workload.id)
        .then((response) => {
          this.loading = false;
          this.workload.next_action = "DELETE";
          this.info = "workload successfully deleted";
          setTimeout(() => this.close(), 3000);
        })
        .catch((err) => {
          console.log(err);
          this.loading = false;
          this.error = err.response.data["error"];
        });
    },
  },
};
</script>
