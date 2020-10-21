<template>
  <base-dialog
    title="Add escalation email"
    v-model="dialog"
    :error="error"
    :loading="loading"
  >
    <template #default>
      <v-form>
        <v-text-field v-model="form.email" label="email" dense></v-text-field>
      </v-form>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text @click="submit">Add</v-btn>
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
      this.$api.escalationEmails
        .add(this.form.email)
        .then((response) => {
          this.done("Email is added");
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
