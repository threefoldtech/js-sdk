<template>
  <div>
    <base-dialog :title="title" v-model="dialog" :loading="loading">
      <template #default>
        <code-area mode="python" :content="json"></code-area>
      </template>
      <template #actions>
        <v-btn v-if="data.Name !== undefined" text color="error" @click.stop="cancel()">Delete Reservation</v-btn>
        <v-btn text @click="close">Close</v-btn>
      </template>
    </base-dialog>
    <cancel-solution v-model="dialogs.cancelSolution" :wids="data.wids"></cancel-solution>
  </div>
</template>

<script>
module.exports = {
  components: {
    "cancel-solution": httpVueLoader("./CancelSolution.vue"),
  },
  props: { data: Object },
  mixins: [dialog],
  data() {
    return {
      dialogs: {
        cancelSolution: false,
      },
    };
  },
  computed: {
    json() {
      return JSON.stringify(this.data, null, 2);
    },
    title() {
      return this.data.Name === undefined
        ? "Workload details"
        : "Solution details";
    },
  },
  methods: {
    cancel() {
      this.dialogs.cancelSolution = true;
    },
  },
};
</script>
