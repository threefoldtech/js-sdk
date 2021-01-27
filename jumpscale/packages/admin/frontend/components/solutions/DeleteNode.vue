<template>
  <base-dialog
    title="Delete Worker"
    v-model="dialog"
    :error="error"
    :loading="loading"
  >
    <template #default>
      Are you sure you want to delete worker, this action can't be undone?
      Please type <b class="font-weight-black">{{ wid }}</b> to confirm.
      <v-text-field v-model="confirmwid" dense></v-text-field>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text color="error" @click="submit" :disabled="disableSubmit"
        >Confirm</v-btn
      >
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  computed: {
    disableSubmit() {
      if (this.confirmwid === this.wid.toString()) {
        return false;
      }
      return true;
    },
  },
  data() {
    return {
      confirmwid: "",
    };
  },
  mixins: [dialog],
  props: ["wid"],
  methods: {
    submit() {
      this.loading = true;
      return this.$api.solutions
        .cancelWorkload(this.wid)
        .then(() => {
          console.log("Worker has been deleted successfully");
          this.close();
          this.$router.go(0);
        })
        .catch((err) => {
          console.log(err);
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
};
</script>
