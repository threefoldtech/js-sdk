<template>
  <external :url="url"></external>
</template>

<script>
module.exports = {
  props: { topic: String },
  computed: {
    url() {
      return `/vdc_dashboard/chats/${this.topic}?noheader=yes`;
    },
  },
  mounted() {
    if (window.marketplace_chatflow_end_listener_set === undefined) {
      // avoid setting multiple listeners
      window.marketplace_chatflow_end_listener_set = true;
      window.addEventListener("message", (event) => {
        let message = "chat ended: ";
        let len = message.length;
        if (
          event.origin != location.origin ||
          event.data.slice(0, len) != message
        )
          return;
        let topic = event.data.slice(len);
        if (topic === "extend_kubernetes") {
          this.$router.push({
            name: "VDCSettings",
          });
        } else if (topic === "extend_storage") {
          this.$router.push({
            name: "VDCSettings",
          });
        } else if (topic === "vmachine") {
          this.$router.push({
            name: "VDCSettings",
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
