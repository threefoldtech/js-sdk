<template>
  <external :url="url"></external>
</template>

<script>
module.exports = {
  props: {
    topic: String,
    tname: {
      type: String,
      default: "",
    },
  },
  computed: {
    url() {
      if (this.tname != "") {
        return `/vdc/chats/${this.topic}#/?noheader=yes&tname=${this.tname}`;
      } else {
        return `/vdc/chats/${this.topic}#/?noheader=yes`;
      }
    },
  },
  mounted() {
    if (window.vdc_chatflow_end_listener_set === undefined) {
      // avoid setting multiple listeners
      window.vdc_chatflow_end_listener_set = true;
      window.addEventListener("message", (event) => {
        let message = "chat ended: ";
        let len = message.length;
        if (
          event.origin != location.origin ||
          event.data.slice(0, len) != message
        )
          return;
        this.$router.push({
          name: "Workloads",
        });
      });
    }
  },
};
</script>
