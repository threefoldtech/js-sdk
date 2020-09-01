<template>
  <external :url="url"></external>
</template>

<script>
  module.exports = {
    props: {topic: String},
    computed: {
      url () {
        return `/threebot_deployer/chats/${this.topic}?noheader=yes`
      }
    },
    mounted() {

      if(window.threebot_deployer_chatflow_end_listener_set === undefined) { // avoid setting multiple listeners
        window.threebot_deployer_chatflow_end_listener_set = true
        window.addEventListener("message", event => {
          let message = "chat ended"
          if(event.origin != location.origin || event.data != message)
            return;
          this.$router.push({
            name: "Workloads",
          })
        })
      }
    }
  }
</script>
