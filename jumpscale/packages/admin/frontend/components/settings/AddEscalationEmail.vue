<template>
  <base-dialog
    title="Add escalation email"
    v-model="dialog"
    :error="error"
    :loading="loading"
  >
    <template #default>
      <v-form>
        <v-text-field
          v-model="form.email"
          label="email"
          :rules="emailRules"
          dense
        ></v-text-field>
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
  data() {
    return {
      emailRules: [
        (v) => !!v || "E-mail is required",
        (v) => /.+@.+\..+/.test(v) || "E-mail must be valid",
      ],
    };
  },
  mixins: [dialog],
  methods: {
    is_email_valid() {
      console.log(this.form.email && /.+@.+\..+/.test(this.form.email));
      if (this.form.email && /.+@.+\..+/.test(this.form.email)) {
        return true;
      } else {
        return false;
      }
    },
    submit() {
      this.loading = true;
      this.error = null;
      if (!this.is_email_valid()) {
        console.log("Email is not valid");
        this.loading = false;
        return;
      }
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
