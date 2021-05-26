<template>
  <base-dialog
    title="Edit Key"
    v-model="dialog"
    :error="error"
    :loading="loading"
  >
    <template #default>
      <v-form ref="form">
        <v-select
          v-model="form.role"
          label="Select Role"
          :items="roles"
          :rules="[(v) => !!v || 'Role is required']"
          required
        ></v-select>
      </v-form>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text @click="submit">Submit</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  mixins: [dialog],
  props: ["name"],
  data() {
    return {
      roles: USER_ROLES,
    };
  },
  methods: {
    submit() {
      this.error = null;
      if (this.$refs.form.validate()) {
        this.loading = true;
        this.$api.apikeys
          .edit(this.name, this.form.role)
          .then((response) => {
            this.done("Key is edited");
            this.$refs.form.resetValidation();
          })
          .catch((error) => {
            this.error = error.response.data;
          })
          .finally(() => {
            this.loading = false;
          });
      }
    },
  },
};
</script>
