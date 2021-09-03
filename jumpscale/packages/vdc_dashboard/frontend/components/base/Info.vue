<template>
  <base-dialog title="Application details" v-model="dialog" :loading="loading">
    <template #default>
      <json-renderer
        title="App details"
        :jsonobj="data"
        :ignored="KeysIgnored"
        :typedict="[...KeysWithTypeDict, ...keyswithtypedictprop]"
      ></json-renderer>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  data() {
    return {
      dialogs: {
        cancelSolution: false,
      },
      tab: 0,
      KeysIgnored: ["Status Details", "User Supplied Values"],
      KeysWithTypeDict: ["progress"],
    };
  },
  props: {
    data: Object,
    keyswithtypedictprop: { type: Array, default: () => [] },
  },
  mixins: [dialog],
};
</script>
