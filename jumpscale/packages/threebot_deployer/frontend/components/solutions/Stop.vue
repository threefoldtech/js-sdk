<template>
  <action-confirmation v-model="dialog" title="Stop 3Bot" api="stopThreebot" :data="data" :messages="messages"></action-confirmation>
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
        confirmationMsg: "This will stop your running 3Bot.",
        successMsg: "3Bot stopped"
      }
    };
  },
};
</script>
