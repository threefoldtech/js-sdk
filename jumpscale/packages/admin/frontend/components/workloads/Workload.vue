<template>
  <div>
    <base-dialog title="Workload Details" v-model="dialog" :loading="loading">
      <template #default>
        <v-tabs v-model="tab" background-color="transparent" color="basil" grow>
          <v-tab :key="'Workload'">Workload</v-tab>
          <v-tab :key="'moredetails'">More details</v-tab>

          <v-tab-item :key="'Workload'">
            <v-simple-table>
              <template v-slot:default>
                <tbody>
                  <tr v-for="(item, key)  in workload" :key="key">
                    <th v-if="!KeysIgnored.includes(key) && item !== ''">{{ key }}</th>
                    <td v-if="KeysWithTypeList.includes(key)" class="pt-2">
                      <v-chip class="ma-1" v-for="node in item" :key="node">{{ node }}</v-chip>
                    </td>
                    <td v-else-if="KeysWithTypeDict.includes(key)" class="pt-2">
                      <v-chip
                        class="ma-1"
                        v-for="(subItem, subkey) in item"
                        :key="subkey"
                      >{{ subkey }} : {{ subItem }}</v-chip>
                    </td>
                    <td v-else-if="!KeysIgnored.includes(key) && item !== ''">{{ item }}</td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
          </v-tab-item>
          <v-tab-item :key="'moredetails'">
            <v-card flat>
              <json-tree :raw="JSON.stringify(workload)"></json-tree>
            </v-card>
          </v-tab-item>
        </v-tabs>
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
      tab: 0,
      KeysWithTypeList: ["ips"],
      KeysWithTypeDict: ["capacity", "network_connection"],
      KeysIgnored: [
        "wireguard_private_key_encrypted",
        "peers",
        "iprange",
        "info",
        "environment",
        "secret_environment",
        "stats_aggregator",
        "logs",
        "secret",
        "password",
        "volumes",
      ],
    };
  },
  computed: {
    cancel_button() {
      return !(
        this.workload.next_action == "DELETE" ||
        this.workload.next_action == "DELETED"
      );
    },
  },
  methods: {
    cancel() {
      this.dialogs.cancelWorkload = true;
    },
  },
  updated() {
    this.tab = 0;
  },
};
</script>
