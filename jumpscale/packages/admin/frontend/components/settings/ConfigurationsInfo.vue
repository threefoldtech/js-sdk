<template>
  <div>
    <base-dialog title="3Bot Configurations" v-model="dialog" :loading="loading">
      <template #default>
        <json-renderer
          title="Configurations"
          :jsonobj="data"
          :ignored="KeysIgnored"
          :typedict="KeysWithTypeDict"
        ></json-renderer>
      </template>
      <template #actions>
        <v-btn text @click="close">Close</v-btn>
      </template>
    </base-dialog>
  </div>
</template>

<script>
module.exports = {
  props: { data: Object },
  mixins: [dialog],
  data() {
    return {
      dialogs: {
        cancelSolution: false,
      },
      KeysIgnored: ["logging", "stores"],
      KeysWithTypeDict: [
        "factory",
        "threebot",
        "alerts",
      ],
    };
  },
};
</script>
