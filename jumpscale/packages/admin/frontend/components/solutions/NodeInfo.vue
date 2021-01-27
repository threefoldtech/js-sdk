<template>
  <base-dialog title="Application details" v-model="dialog" :loading="loading">
    <template #default>
      <json-renderer
        title="App details"
        :jsonobj="data"
        :ignored="KeysIgnored"
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
    };
  },
  props: { data: Object },
  mixins: [dialog],
};
</script>
