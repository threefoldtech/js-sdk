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
      Are you sure you want to Destroy {{ data.Name }}?
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
      this.loading = true;
      this.error = null;
      this.$api.solutions
        .destroyThreebot(this.data.solution_uuid)
        .then((response) => {
          this.alert("3bot Destroyed", "success");
          this.$router.go(0);
        })
        .catch((err) => {
          this.alert("Failed to destroy 3Bot", "error");
          this.close();
        });
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
