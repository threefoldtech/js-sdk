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
          let message = "chat ended"
          if(event.origin != location.origin || event.data != message)
            return;
          if(this.topic == "pools"){
            this.$router.push({
              name: "Capacity Pools"
            })
          }else{
            this.$router.push({
              name: "Solution",
              params: {type: this.topic}
            })
          }
        })
      }
    }
  }
</script>
