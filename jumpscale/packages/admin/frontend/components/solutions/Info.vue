<template>
  <div>
    <base-dialog :title="title" v-model="dialog" :loading="loading">
      <template #default>
        <v-tabs v-model="tab" background-color="transparent" color="basil" grow>
          <v-tab :key="title">{{ title }}</v-tab>
          <v-tab :key="'moredetails'">More details</v-tab>

          <v-tab-item :key="title">
            <v-simple-table>
              <template v-slot:default>
                <tbody>
                  <tr v-for="(item, key)  in json" :key="key">
                    <th>{{ key }}</th>
                    <td
                      v-if="key === 'Node ids' || key === 'wids' || key === 'Active workload ids'"
                      class="pt-2"
                    >
                      <v-chip class="ma-1" v-for="node in item" :key="node">{{ node }}</v-chip>
                    </td>
                    <td v-else-if="key === 'nodes'">
                      <v-chip
                        class="ma-1"
                        v-for="(ip, node) in item"
                        :key="node"
                      >{{ ip }} / ({{ node }})</v-chip>
                    </td>
                    <td v-else>{{ item }}</td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
          </v-tab-item>
          <v-tab-item :key="'moredetails'">
            <v-card flat>
              <json-tree :raw="JSON.stringify(json)"></json-tree>
            </v-card>
          </v-tab-item>
        </v-tabs>
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
    "cancel-solution": httpVueLoader("./CancelSolution.vue"),
  },
  props: { data: Object },
  mixins: [dialog],
  data() {
    return {
      dialogs: {
        cancelSolution: false,
      },
      tab: 0,
    };
  },
  computed: {
    json() {
      if (this.data.last_updated !== undefined)
        this.data.last_updated = new Date(this.data.last_updated * 1000);
      if (this.data.empty_at !== undefined)
        this.data.empty_at = new Date(this.data.empty_at * 1000);
      return this.data;
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
