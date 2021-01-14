<template>
  <action-confirmation v-model="dialog" title="Destroy 3Bot" api="destroyThreebot" :data="data" :messages="messages" ></action-confirmation>
</template>

<script>
module.exports = {
  components: {
    "action-confirmation": httpVueLoader("./ActionConfirmation.vue"),
  },
  mixins: [dialog],
  props: { data: Object },
  data() {
    return {
      messages: {
        confirmationMsg: "This will stop your running 3Bot and delete all backups.",
        successMsg: "3Bot destroyed"
      }
    };
  },
};
</script>
