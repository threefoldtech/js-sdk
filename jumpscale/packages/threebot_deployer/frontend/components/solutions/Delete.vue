<template>
  <action-confirmation v-model="dialog" title="Destroy 3Bot" api="destroyThreebot" :data="data"></action-confirmation>
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
