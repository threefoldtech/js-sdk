<template>
  <div>
    <base-dialog title="Workload Details" v-model="dialog" :loading="loading">
      <template #default>
        <json-renderer
          title="Workload"
          :jsonobj="workload"
          :ignored="KeysIgnored"
          :typelist="KeysWithTypeList"
          :typedict="KeysWithTypeDict"
        ></json-renderer>
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
};
</script>
