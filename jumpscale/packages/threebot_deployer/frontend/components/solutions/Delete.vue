<template>
  <base-dialog
    v-if="data"
    title="Cancel Workload"
    v-model="dialog"
    :error="error"
    :info="info"
    :warning="warning"
    :loading="loading"
  >
    <template #default>
      Are you sure you want to cancel {{data.Name}}?
      <v-checkbox v-model="deleteBackup" :label="`Delete Backup`" @click="warningShow()"></v-checkbox>
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
      deleteBackup: null,
      lastThreebotSelected: "",
    };
  },
  props: { data: Object },
  methods: {
    submit() {
      this.loading = true;
      this.error = null;
      this.$api.solutions
        .cancelReservation(this.data.wids)
        .then((response) => {
          if (this.deleteBackup) {
            this.$api.solutions
              .destroyBackup(
                `${this.data.Owner.split(".")[0]}_${this.data.Name}`
              )
              .then((response) => {
                this.alert("Cancelled 3Bot with delete its backup", "success");
                this.$router.go(0);
              })
              .catch((err) => {
                this.alert(
                  "Cancelled 3But but failed to delete backup",
                  "error"
                );
                this.$router.go("Workloads");
              });
          } else {
            this.alert("Cancelled 3Bot", "success");
            this.$router.go(0);
          }
        })
        .catch((err) => {
          this.alert("Failed to cancel 3Bot", "error");
          this.close();
        });
    },
    warningShow() {
      if (this.deleteBackup) {
        this.warning =
          "Warning: If you delete backup, you can't restore your 3Bot again.";
      } else {
        this.warning = "";
      }
    },
  },
  updated() {
    if (this.lastThreebotSelected !== this.data.Name) {
      this.deleteBackup = false;
      this.warning = "";
      this.lastThreebotSelected = this.data.Name;
    }
  },
};
</script>
