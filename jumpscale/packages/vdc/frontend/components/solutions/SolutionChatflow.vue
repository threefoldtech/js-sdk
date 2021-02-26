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
      let res = ""
      if (this.tname != "") {
        res = `/vdc/chats/${this.topic}#/?noheader=yes&tname=${this.tname}`;
      } else {
        res = `/vdc/chats/${this.topic}#/?noheader=yes`;
      }
      if (location.search){
        res += "&" + location.search.slice(1)
      }
      return res
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
