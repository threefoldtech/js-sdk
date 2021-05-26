<template>
  <div>
    <base-dialog
      title="Generate Key"
      v-model="dialog"
      :error="error"
      :loading="loading"
    >
      <template #default>
        <v-form ref="form">
          <v-text-field
            v-model="form.name"
            label="Key name"
            :rules="nameRules"
            required
          ></v-text-field>
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
        <v-btn text @click="submit">Generate</v-btn>
      </template>
    </base-dialog>
    <show-key
      v-model="dialogs.showKey"
      :apikey="key"
    ></show-key>
  </div>
</template>

<script>
module.exports = {
  mixins: [dialog],
  components: {
    "show-key": httpVueLoader("./ShowKey.vue"),
  },
  data() {
    return {
      key: null,
      dialogs: {
        showKey: false,
      },
      roles: USER_ROLES,
      regex: /^[a-z]([a-z0-9]*)$/,
      nameRules: [
        (v) => !!v || "Name is required",
        (v) =>
          (v && this.regex.test(v)) ||
          "Invalid value. It should be a valid identifier, all lowercase and starting with a letter, no spaces and no special characters",
      ],
    };
  },
  methods: {
    submit() {
      this.error = null;
      if (this.$refs.form.validate()) {
        this.loading = true;
        this.$api.apikeys
          .generate(this.form.name, this.form.role)
          .then((response) => {
            this.key = response.data.data.key;
            this.dialogs.showKey = true;
            this.done("Key is generated");
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
