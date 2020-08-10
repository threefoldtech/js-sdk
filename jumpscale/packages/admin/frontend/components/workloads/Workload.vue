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
      <v-btn text @click="cancel(data.id)">Cancel Workload</v-btn>
    </template>
    </base-dialog>
  </div>
</template>

<script>

module.exports = {
  props: {data: Object},
  mixins: [dialog],
  methods: {
    cancel (wid) {
        this.$api.solutions.cancelWorkload(wid).then((response) => {
          window.location.reload();
        })
      },
  }
}
</script>
