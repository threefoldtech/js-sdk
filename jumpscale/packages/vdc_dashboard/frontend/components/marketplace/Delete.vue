<template>
  <base-dialog
    title="Cancel workload"
    v-model="dialog"
    :error="error"
    :loading="loading"
  >
    <template #default>
      Are you sure you want to cancel {{ releasename }}?
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
  props: ["releasename", "solutionid", "vdcname", "namespace"],
  methods: {
    submit() {
      let quantumStorageSolutions = ["minio"]; // TODO: add all quantum storage solutions here
      this.loading = true;
      this.error = null;
      var usesQuantumStorage = null;
      quantumStorageSolutions.forEach((element) => {
        if (this.namespace.includes(element)) {
          usesQuantumStorage = true;
          break;
        }
      });
      this.$api.solutions
        .deleteSolution(
          this.releasename,
          this.solutionid,
          this.vdcname,
          this.namespace,
          usesQuantumStorage
        )
        .then((response) => {
          console.log("cancelled");
          this.$router.go(0);
        })
        .catch((err) => {
          console.log("failed");
          this.close();
        });
    },
  },
};
</script>
