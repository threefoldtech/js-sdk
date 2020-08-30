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
                    <td v-if="KeysWithTypeList.includes(key)" class="pt-2">
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
    "cancel-solution": httpVueLoader("./Delete.vue"),
  },
  data() {
    return {
      dialogs: {
        cancelSolution: false,
      },
      tab: 0,
    };
  },
  props: { data: Object },
  mixins: [dialog],
  computed: {
    json() {
      return this.data;
    },
    title() {
      return this.data.Name === undefined
        ? "Workload details"
        : "Solution details";
    },
    KeysWithTypeList() {
      return ["Node ids", "wids", "Active workload ids"];
    },
  },
  methods: {
    cancel() {
      this.dialogs.cancelSolution = true;
    },
  },
};
</script>
