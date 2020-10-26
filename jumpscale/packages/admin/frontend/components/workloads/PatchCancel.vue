<template>
  <base-dialog
    title="Cancel selected workloads"
    v-model="dialog"
    :error="error"
    :info="info"
    :warning="warning"
    :loading="loading"
  >
    <template #default v-if="!deleted">Are you sure you want to cancel all {{ selected.length }} selected workloads?</template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text color="error" @click="submit">Confirm</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  mixins: [dialog],
  props: ["selected"],
  data(){
    return {
      deleted : false
    };
  },
  methods: {
    submit() {
      this.loading = true;
      this.error = null;
      this.info = null;
      this.warning = null;

      let wids = [];
      for (i = 0; i < this.selected.length; i++) {
        if (
          this.selected[i].next_action == "DELETE" ||
          this.selected[i].next_action == "DELETED"
        ) {
          continue;
        }
        wids.push(this.selected[i].id);
      }
      if (wids.length === 0) {
        this.loading = false;
        this.deleted = true;
        this.warning = "All selected workloads are already deleted";
        setTimeout(() => {
          this.deleted = false;
          this.close();
        }, 2000);
      }
      else {
        this.$api.solutions
        .patchCancelWorkload(wids)
        .then((response) => {
          for (let i = 0; i < this.selected.length; i++) {
            this.selected[i].next_action = "DELETE";
          }

          this.loading = false;
          this.deleted = true;
          this.info = "workloads successfully deleted";
          setTimeout(() => {
            this.deleted = false;
            this.close();
          }, 3000);
          this.deleted = false;
        })
        .catch((err) => {
          console.log(err);
          this.loading = false;
          this.error = err.response.data["error"];
        });
      }
    },
    cancel() {
      this.close();
    },
  },
};
</script>
