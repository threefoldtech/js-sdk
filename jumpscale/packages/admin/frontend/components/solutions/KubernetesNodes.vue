<template>
  <div>
    <div class="actions mb-3">
      <h1 class="d-inline" color="primary" text>Compute Nodes</h1>

      <v-btn
        class="float-right p-4"
        color="primary"
        text
        @click.stop="openChatflow('extend_kube', k8sNodes[0].wid)"
      >
        <v-icon left>mdi-plus</v-icon>Add node
      </v-btn>
    </div>

    <v-data-table
      :headers="headers"
      :items="k8sNodes"
      :loading="loading"
      class="elevation-1"
    >
      <template slot="no-data">No Nodes available</template>
      <template v-slot:item.wid="{ item }">
        <div>{{ item.wid }}</div>
      </template>

      <template v-slot:item.public_ip="{ item }">
        <div v-if="item.public_ip != '::/128'">{{ item.public_ip }}</div>
        <div v-else></div>
      </template>

      <template v-slot:item.ip="{ item }">
        <div v-if="item.ip_address != '::/128'">{{ item.ip_address }}</div>
        <div v-else></div>
      </template>

      <template v-slot:item.role="{ item }">
        <div>{{ item.role }}</div>
      </template>

      <template v-slot:item.vcpu="{ item }">
        <div>{{ item.CPU }}</div>
      </template>

      <template v-slot:item.memory="{ item }">
        <div>{{ item.Memory }}</div>
      </template>

      <template v-slot:item.storage="{ item }">
        <div>{{ item.storage }}</div>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-tooltip top>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="open(item)">
              <v-icon v-bind="attrs" v-on="on" color="#206a5d"
                >mdi-information-outline</v-icon
              >
            </v-btn>
          </template>
          <span>Show Information</span>
        </v-tooltip>

        <v-tooltip top v-if="item.role !== 'master'">
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="deleteNode(item.wid)">
              <v-icon v-bind="attrs" v-on="on" color="#810000"
                >mdi-delete</v-icon
              >
            </v-btn>
          </template>
          <span>Delete</span>
        </v-tooltip>
      </template>
    </v-data-table>
    <solution-info
      v-if="selected"
      v-model="dialogs.info"
      :data="selected"
    ></solution-info>
    <cancel-workload
      v-if="selectedworker"
      v-model="dialogs.cancelWorkload"
      :wid="selectedworker"
    ></cancel-workload>
  </div>
</template>

<script>
module.exports = {
  components: {
    "solution-info": httpVueLoader("./NodeInfo.vue"),
    "cancel-workload": httpVueLoader("./DeleteNode.vue"),
  },
  props: ["k8sName"],

  data() {
    return {
      loading: true,
      selected: null,
      selectedworker: null,
      dialogs: {
        info: false,
        cancelWorkload: false,
      },
      k8sNodes: [],
      headers: [
        { text: "WID", value: "wid" },
        { text: "IP Address", value: "ip" },
        { text: "Public IP", value: "public_ip" },
        { text: "Role", value: "role" },
        { text: "vCPU", value: "vcpu" },
        { text: "Memory", value: "memory" },
        { text: "Disk Size", value: "storage" },
        { text: "Actions", value: "actions", sortable: false },
      ],
    };
  },
  methods: {
    openChatflow(topic, master_wid) {
      let queryparams = { master_wid: master_wid };
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: topic, queryparams: queryparams },
      });
    },
    open(record) {
      this.selected = record;
      this.dialogs.info = true;
    },
    deleteNode(wid) {
      this.selectedworker = wid;
      this.dialogs.cancelWorkload = true;
    },
    getK8sDetails(k8sSolutionName) {
      if (k8sSolutionName) {
        this.$api.solutions
          .getK8sDetails(k8sSolutionName)
          .then((response) => {
            this.k8sNodes = JSON.parse(response.data).data;
          })
          .finally(() => {
            this.loading = false;
          });
      }
    },
  },
  mounted() {
    this.getK8sDetails(this.k8sName);
  },
};
</script>

<style scoped>
h1 {
  color: #1b4f72;
}
</style>
