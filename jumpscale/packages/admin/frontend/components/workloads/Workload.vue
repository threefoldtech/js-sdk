<template>
  <div>
    <base-dialog title="Workload Details" v-model="dialog" :loading="loading">
      <template #default>
          <v-simple-table>
              <template v-slot:default>
                <tbody>
                    <tr v-for="(item, key) in data" :key="key">
                        <th>{{ key }}</th>
                        <td> {{ item }} </td>
                    </tr>
                </tbody>
              </template>
      </template>
      <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text color="error" @click="cancel()">Cancel Workload</v-btn>
    </template>
    </base-dialog>
    <cancel-workload v-model="dialogs.cancelWorkload" v-if="data" :wid="data.id"></cancel-workload>
  </div>
</template>

<script>

module.exports = {
  props: {data: Object},
  mixins: [dialog],
  components: {
    "cancel-workload": httpVueLoader("./CancelWorkload.vue"),
  },
  data() {
    return {
      dialogs: {
        cancelWorkload: false,
      },
      wid:null,
    };
  },
  methods: {
    cancel () {
        this.dialogs.cancelWorkload = true;
      },
  }
}
</script>
