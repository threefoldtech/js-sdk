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
  props:{
    title: String,
    api: String,
    wid: Number,
    messages: Object,
  },
  methods: {
    submit() {
        this.loading = true;
        this.error = null;
        this.$api.solutions
            [this.api](this.wid)
            .then((response) => {
            this.alert(this.messages.successMsg, "success");
            this.$router.go(0);
            }).catch((err) => {
            this.error = err.response.data["error"];
            this.alert(this.error , "error");
            }).finally(() => {
            this.loading = false;
            });
    },
  },

};
</script>
