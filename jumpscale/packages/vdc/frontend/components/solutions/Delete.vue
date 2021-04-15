<template>
  <base-dialog
    title="Delete VDC"
    v-model="dialog"
    :error="error"
    :loading="loading"
  >
    <template #default>
      Are you sure you want to delete this VDC, this action can't be undone?
      <br />
      <strong class="red--text text--lighten-1">
        WARNING: This action can't be undone. Please make sure to transfer the
        tokens left in your wallet before deletion. (Wallet secret is available
        in your VDC dashboard wallet pane, and it can be imported into any stellar compatible wallet.)
      </strong>
      <br /><br />
      Please type <b class="font-weight-black">{{ vdcname }}</b> to confirm.
      <v-text-field v-model="confirmvdc" dense></v-text-field>
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
      if (this.confirmvdc === this.vdcname.toString()) {
        return false;
      }
      return true;
    },
  },
  data() {
    return {
      confirmvdc: "",
    };
  },
  mixins: [dialog],
  props: ["vdcname"],
  methods: {
    submit() {
      this.loading = true;
      return this.$api.solutions
        .deleteVDC(this.vdcname)
        .then(() => {
          console.log("VDC has been deleted successfully");
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
