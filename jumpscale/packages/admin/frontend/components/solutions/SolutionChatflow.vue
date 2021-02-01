<template>
  <external :package="package" :name="name" :url="url"></external>
</template>

<script>
module.exports = {
  props: {
    topic: String,
    queryparams: { type: Object, default: null },
  },
  data() {
    return {
      package: true,
      name: "chatflows",
    };
  },
  computed: {
    url() {
      if (this.queryparams !== null) {
        let chatflowUrl = `/chatflows/tfgrid_solutions/chats/${this.topic}#/?`;
        Object.keys(this.queryparams).forEach((key) => {
          chatflowUrl += `${key}=${this.queryparams[key]}&`;
        });
        return chatflowUrl;
      } else {
        return `/chatflows/tfgrid_solutions/chats/${this.topic}`;
      }
    },
  },
  mounted() {
    if (window.admin_chatflow_end_listener_set === undefined) {
      // avoid setting multiple listeners
      window.admin_chatflow_end_listener_set = true;
      window.addEventListener("message", (event) => {
        let message = "chat ended: ";
        let len = message.length;
        if (
          event.origin != location.origin ||
          event.data.slice(0, len) != message
        )
          return;
        let topic = event.data.slice(len);
        if (topic === "pools" || topic === "extend_pools") {
          this.$router.push({
            name: "Capacity Pools",
          });
        } else if (topic === "network_access") {
          this.$router.push({
            name: "Solution",
            params: { type: "network" },
          });
        } else if (topic === "extend_kube") {
          this.$router.push({
            name: "Solution",
            params: { type: "kubernetes" },
          });
        } else {
          this.$router.push({
            name: "Solution",
            params: { type: topic },
          });
        }
      });
    }
  },
};
</script>
