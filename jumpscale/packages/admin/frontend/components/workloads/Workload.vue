<template>
  <div>
    <base-dialog title="Workload Details" v-model="dialog" :loading="loading">
      <template #default>
        <v-simple-table>
          <template v-slot:default>
            <tbody>
              <tr v-for="(item, key) in workload" :key="key">
                <th>{{ key }}</th>
                <td>{{ item }}</td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </template>
      <template #actions>
        <v-btn text @click="close">Close</v-btn>
        <v-btn text color="error" v-if="cancel_button" @click="cancel()">Cancel workload</v-btn>
      </template>
    </base-dialog>
    <cancel-workload v-model="dialogs.cancelWorkload" v-if="workload" :workload="workload"></cancel-workload>
  </div>
</template>

<script>
module.exports = {
  props: { workload: Object },
  mixins: [dialog],
  components: {
    "cancel-workload": httpVueLoader("./CancelWorkload.vue"),
  },
  data() {
    return {
      dialogs: {
        cancelWorkload: false,
      },
    };
  },
  computed: {
      cancel_button() {
        return !(this.workload.next_action == "DELETE" || this.workload.next_action == "DELETED")
      },
  },
  methods: {
    cancel() {
      this.dialogs.cancelWorkload = true;
    },
  },
};
</script>
