<template>
  <base-dialog
    v-if="data"
    title="Stop Workload"
    v-model="dialog"
    :error="error"
    :info="info"
    :warning="warning"
    :loading="loading"
  >
    <template #default>
      Are you sure you want to stop {{ data.name }}?
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
        .stopThreebot(this.data.solution_uuid)
        .then((response) => {
          this.alert("Stopped 3Bot", "success");
          this.$router.go(0);
        })
        .catch((err) => {
          this.alert("Failed to Stop 3Bot", "error");
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
