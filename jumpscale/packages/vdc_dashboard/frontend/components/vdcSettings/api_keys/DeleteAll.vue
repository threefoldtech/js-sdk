<template>
  <base-dialog
    title="Remove All Keys"
    v-model="dialog"
    :error="error"
    :loading="loading"
  >
    <template #default>
      Are you sure you want to remove all API Keys?
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
  methods: {
    submit() {
      this.loading = true;
      this.error = null;
      this.$api.apikeys
        .deleteAll()
        .then((response) => {
          this.done("All Keys are removed");
        })
        .catch((error) => {
          this.error = error.response.data;
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
};
</script>
