<template>
  <v-card flat height="100%" class="pa-5" outlined>
    <v-card-text>
      <p class="display-1 text--primary">Threefold Marketplace</p>
      <div class="text--primary">
        Marketplace is an experience to demonstrate the ability of
        <a
          target="_blank"
          href="https://threefold.io/"
        >Threefold grid</a> as an enabling infrastructure of an open-source,
        enabling bootstrapping personal threebot and the deployment of opensource solutions (Minio, gitea, kubernetes, ubuntu, web publishing platform, ..)
        on the
        <a
          target="_blank"
          href="https://threefold.io/"
        >Threefold grid</a>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
module.exports = {
  mounted() {
    this.$root.$emit("sidebar", true);
  },
};
</script>
