<template>
  <action-confirmation v-model="dialog" title="Stop 3Bot" api="stopThreebot" :data="data"></action-confirmation>
</template>

<script>
module.exports = {
  components: {
    "action-confirmation": httpVueLoader("./ActionConfirmation.vue"),
  },
  mixins: [dialog],
  props: { data: Object },
};
</script>
