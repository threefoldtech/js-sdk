<template>
  <external :package="package" :name="name" :url="url"></external>
</template>

<script>
  module.exports = {
    props: {topic: String},
    data () {
      return {
        package: true,
        name: "chatflows",
      }
    },
    computed: {
      url () {
        return `/chatflows/tfgrid_solutions/chats/${this.topic}`
      }
    },
    mounted() {
      if(window.admin_chatflow_end_listener_set === undefined) { // avoid setting multiple listeners
        window.admin_chatflow_end_listener_set = true
        window.addEventListener("message", event => {
          let message = "chat ended: "
          let len = message.length
          if(event.origin != location.origin || event.data.slice(0, len) != message)
            return;
          let topic = event.data.slice(len)
          if(topic == "pools"){
            this.$router.push({
              name: "Capacity Pools"
            })
          }else{
            this.$router.push({
              name: "Solution",
              params: {type: topic}
            })
          }
        })
      }
    }
  }
</script>
