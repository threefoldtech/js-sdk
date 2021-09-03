<template>
  <base-dialog
    v-if="wid"
    :title="title"
    v-model="dialog"
    :error="error"
    :loading="loading"
    :persistent="true"
  >
    <template #default>
      {{ messages.confirmationMsg }}
      <v-alert v-if="messages.warningMsg" border="top" colored-border type="warning" elevation="2">
        <span v-html="messages.warningMsg"></span>
      </v-alert>
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
  props: {
    title: String,
    api: String,
    wid: Number,
    messages: Object,
    releasestodelete: Array
  },
  methods: {
    submit() {
      this.loading = true;
      this.error = null;
      this.$api.solutions[this.api](this.wid, this.releasestodelete)
        .then((response) => {
          this.alert(this.messages.successMsg, "success");
          this.close();
          this.loading = false;
          this.getlist();
        })
        .catch((err) => {
          this.error = err.response.data["error"];
          this.alert(this.error, "error");
        })
        .finally(() => {
          this.loading = false;
        });
    },
    getlist() {
      this.$emit("reload-vdcinfo", {
        message: "VDC info has been reloaded successfully!",
      });
    },
  },
};
</script>
