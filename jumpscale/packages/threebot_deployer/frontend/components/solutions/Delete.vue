<template>
  <base-dialog
    v-if="data"
    title="Destroy Workload"
    v-model="dialog"
    :error="error"
    :info="info"
    :warning="warning"
    :loading="loading"
  >
    <template #default>
      Please enter the password of {{ data.name }}. This will stop your running 3Bot and delete all backups.
      <v-form>
        <v-text-field :type="'password'" v-model="form.password" dense></v-text-field>
      </v-form>
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
  data() {
    return {
      lastThreebotSelected: "",
    };
  },
  props: { data: Object },
  methods: {
    submit() {
      if (!this.form.password) {
        this.error = "Password required!";
      } else {
        this.loading = true;
        this.error = null;
        this.$api.solutions
          .destroyThreebot(this.data.solution_uuid, this.form.password)
          .then((response) => {
            this.alert("3bot Destroyed", "success");
            this.$router.go(0);
          })
          .catch((err) => {
            this.alert("Failed to destroy 3Bot", "error");
            this.close();
          });
      }
    },
  },
  updated() {
    if (this.lastThreebotSelected !== this.data.name) {
      this.warning = "";
      this.lastThreebotSelected = this.data.name;
    }
  },
};
</script>

<style scoped>
form p {
  color: #ec7063 !important;
}
</style>
