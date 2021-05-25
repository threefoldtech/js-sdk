<template>
  <base-dialog
    title="Remove Key"
    v-model="dialog"
    :error="error"
    :loading="loading"
  >
    <template #default>
      Are you sure you want to remove <strong>{{ name }}</strong> from API Keys
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
    submit() {
      this.loading = true;
      this.error = null;
      this.$api.apikeys
        .delete(this.name)
        .then((response) => {
          this.done("Key is removed");
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
