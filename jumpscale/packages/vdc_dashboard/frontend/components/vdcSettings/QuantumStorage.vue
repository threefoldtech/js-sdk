<template>
  <base-dialog title="Confirmation" v-model="dialog" :loading="loading">
    <template #default>
      This will allow you to use quantum storage on your VDC and download the
      ZStor config file. Please make sure to keep the config file safe
    </template>
    <template #actions>
      <v-btn text @click="close">Cancel</v-btn>
      <v-btn text color="error" @click="submit">Enable</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  mixins: [dialog],
  data() {
    return {
      loading: false,
    };
  },
  methods: {
    submit() {
      this.loading = true;
      this.$api.quantumstorage
        .enable()
        .then((response) => {
          const blob = new Blob([response.data.data]);
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", "zstor_config.toml");
          document.body.appendChild(link);
          link.click();
          link.parentNode.removeChild(link);
          this.loading = false;
          this.close();
        })
        .catch((err) => {
          console.log("failed");
          this.close();
        })
        .finally(() => {
          this.loading = false;
          this.close();
        });
    },
  },
};
</script>
