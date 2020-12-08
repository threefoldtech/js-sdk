<template>
  <base-dialog
    title="Email Server Configurations"
    v-model="dialog"
    :error="error"
    :loading="loading"
  >
    <template #default>
      <v-form>
        <v-text-field
          v-model="emailServerConfig.host"
          label="SMTP Host"
          dense
        ></v-text-field>
        <v-text-field
          v-model="emailServerConfig.port"
          label="Port"
          dense
        ></v-text-field>
        <v-text-field
          v-model="emailServerConfig.username"
          label="Username"
          dense
        ></v-text-field>
        <v-text-field
          v-model="emailServerConfig.password"
          label="Password"
          type="password"
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
  mixins: [dialog],
  data() {
    return {
      emailServerConfig: {},
    };
  },
  methods: {
    getEmailServerConfig() {
      this.$api.emailServerConfig.get().then((response) => {
        this.emailServerConfig = JSON.parse(response.data).data;
      });
    },
    submit() {
      this.loading = true;
      this.error = null;
      this.$api.emailServerConfig
        .set(
          this.emailServerConfig.host,
          this.emailServerConfig.port,
          this.emailServerConfig.username,
          this.emailServerConfig.password
        )
        .then((response) => {
          this.done("Email Server config updated");
        })
        .catch((error) => {
          this.error = error.response.data.error;
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
  mounted() {
    this.getEmailServerConfig();
  },
};
</script>
