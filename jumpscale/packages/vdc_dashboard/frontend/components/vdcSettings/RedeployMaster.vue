<template>
  <base-dialog
    title="Redeploy master"
    v-model="dialog"
    :error="error"
    :loading="loading"
  >
    <template #default> Are you sure you want to redeploy master node? </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text @click="submit">Confirm</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  mixins: [dialog],
  props: { wid: Number },
  methods: {
    submit() {
      this.loading = true;
      this.error = null;
      this.$api.solutions
        .redeployMaster(this.wid)
        .then((response) => {
          this.done("Master is redeployed");
        })
        .catch((error) => {
          this.error = error.response.data.error;
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
};
</script>
