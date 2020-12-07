<template>
  <div>
    <base-dialog title="Application details" v-model="dialog" :loading="loading">
      <template #default>
        <json-renderer
          title="App details"
          :jsonobj="data"
          :ignored="KeysIgnored"
        ></json-renderer>
      </template>
      <template #actions>
        <v-btn
          v-if="data.Name !== undefined"
          text
          color="error"
          @click.stop="cancel()"
        >Delete Reservation</v-btn>
        <v-btn text @click="close">Close</v-btn>
      </template>
    </base-dialog>
    <cancel-solution v-model="dialogs.cancelSolution" :wids="data.wids"></cancel-solution>
  </div>
</template>

<script>
module.exports = {
  components: {
    "cancel-solution": httpVueLoader("./Delete.vue"),
  },
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
  methods: {
    cancel() {
      this.dialogs.cancelSolution = true;
    },
  },
};
</script>
