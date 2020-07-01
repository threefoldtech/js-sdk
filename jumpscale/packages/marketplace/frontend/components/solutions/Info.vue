<template>
  <base-dialog title="Solution info" v-model="dialog" :loading="loading">
    <template #default>
      <pre>
        {{JSON.stringify(JSON.parse(data.reservation),null,2)}}
      </pre>
    </template>
    <template #actions>
      <v-btn text color="error" @click.stop="cancel(data.solution_type, data.id)">Cancel</v-btn>
      <v-btn text @click="close">Close</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  props: { data: Object },
  mixins: [dialog],
  methods: {
    cancel(solutionType, solutionId) {
      this.$api.solutions.cancelReservation(solutionType, solutionId).then(response => {
        console.log("cancel")
      }).catch(err => {
        console.log("failed")
      });
    }
  }
};
</script>
