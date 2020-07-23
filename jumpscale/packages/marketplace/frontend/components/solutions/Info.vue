<template>
  <base-dialog title="Solution info" v-model="dialog" :loading="loading">
    <template #default>
      <code-area mode="python" :content="json"></code-area>
      <!-- <pre>
      </pre>-->
    </template>
    <template #actions>
      <v-btn text color="error" @click.stop="cancel(data.solution_type, data.id)">Delete Reservation</v-btn>
      <v-btn text @click="close">Close</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  props: { data: Object },
  mixins: [dialog],
  computed: {
    json() {
      return JSON.stringify(JSON.parse(this.data.reservation), null, 2);
    }
  },
  methods: {
    cancel(solutionType, solutionId) {
      this.$api.solutions
        .cancelReservation(solutionType, solutionId)
        .then(response => {
          console.log("cancel");
          this.$router.go(0);
        })
        .catch(err => {
          console.log("failed");
        });
    }
  }
};
</script>
