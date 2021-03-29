<template>
  <base-dialog title="Download kubeconfig file" v-model="dialog">
    <template #default>
      WARNING: Please keep the kubeconfig file safe and secure. Anyone who has
      this file can access the kubernetes cluster Are you sure to continue
      downloading?
    </template>
    <template #actions>
      <v-btn text @click="close">Cancel</v-btn>
      <v-btn text color="error" @click="submit">Download</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  mixins: [dialog],
  methods: {
    submit() {
      this.$api.solutions
        .getKubeConfig()
        .then((response) => {
          const blob = new Blob([response.data.data]);
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", "config.yaml");
          document.body.appendChild(link);
          link.click();
          link.parentNode.removeChild(link);
          this.close();
        })
        .catch((err) => {
          console.log("failed");
          this.close();
        });
    },
  },
};
</script>
