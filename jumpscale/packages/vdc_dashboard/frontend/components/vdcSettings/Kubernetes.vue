<template>
  <div>
    <div class="actions mb-3">
      <h1 class="d-inline" color="primary" text>Compute Nodes</h1>
      <v-btn
        class="float-right p-4"
        color="primary"
        text
        @click.stop="downloadKubeConfigFile()"
      >
        <v-icon left>mdi-download</v-icon>KubeConfig
      </v-btn>
      <v-btn
        class="float-right p-4"
        color="primary"
        text
        @click.stop="openChatflow('extend_kubernetes')"
      >
        <v-icon left>mdi-plus</v-icon>Add node
      </v-btn>
    </div>

    <v-data-table
      :headers="headers"
      :items="kubernetesData"
      :loading="loading"
      class="elevation-1"
    >
      <template slot="no-data">No VDC instances available</template>
      <template v-slot:item.wid="{ item }">
        <div>{{ item.wid }}</div>
      </template>

      <template v-slot:item.ip="{ item }">
        <div v-if="item.public_ip != '::/128'">{{ item.public_ip }}</div>
        <div v-else></div>
      </template>

      <template v-slot:item.role="{ item }">
        <div>{{ item.role }}</div>
      </template>

      <template v-slot:item.vcpu="{ item }">
        <div>{{ kubernetesSizeMap[item.size].vcpu }}</div>
      </template>

      <template v-slot:item.memory="{ item }">
        <div>{{ kubernetesSizeMap[item.size].memory }} GB</div>
      </template>

      <template v-slot:item.storage="{ item }">
        <div>{{ kubernetesSizeMap[item.size].storage }} GB</div>
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
    
    <template v-if="this.vdc && this.vdc.kubernetes.length < this.vdc.total_capacity">
      <p>The VDC will autoscale to the plan limit.</p>
    </template>
    
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
    <download-kubeconfig v-model="dialogs.downloadKube"></download-kubeconfig>
  </div>
</template>

<script>
module.exports = {
  components: {
    "solution-info": httpVueLoader("../base/Info.vue"),
    "cancel-workload": httpVueLoader("./Delete.vue"),
    "download-kubeconfig": httpVueLoader("./DownloadKubeconfig.vue"),
  },
  props: ["vdc", "loading"],

  data() {
    return {
      selected: null,
      selectedworker: null,
      dialogs: {
        info: false,
        cancelWorkload: false,
        downloadKube: false,
      },
      headers: [
        { text: "WID", value: "wid" },
        { text: "IP Address", value: "ip" },
        { text: "Role", value: "role" },
        { text: "vCPU", value: "vcpu" },
        { text: "Memory", value: "memory" },
        { text: "Disk Size", value: "storage" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      kubernetesSizeMap: KUBERNETES_VM_SIZE_MAP,
    };
  },
  methods: {
    openChatflow(topic) {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: topic },
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

    downloadKubeConfigFile() {
      this.dialogs.downloadKube = true;
    },
  },
  computed: {
    kubernetesData() {
      if (this.vdc) {
        return this.vdc.kubernetes;
      }
    },
  },
};
</script>

<style scoped>
h1 {
  color: #1b4f72;
}
</style>
