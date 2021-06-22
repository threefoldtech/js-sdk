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
      <v-btn
        v-if="!(loading || checkMasterExistence)"
        class="float-right p-4"
        color="primary"
        text
        @click.stop="redeployMaster(null)"
      >
        <v-icon left>mdi-reload</v-icon>Redeploy Master
      </v-btn>
    </div>

    <v-data-table
      :headers="headers"
      :items="kubernetesData"
      :loading="loading || tableLoading"
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
        <v-tooltip top v-if="item.role === 'master' && item.status === false">
              <template v-slot:activator="{ on, attrs }">
                <v-btn icon @click.stop="redeployMaster(item.wid)">
                  <v-icon v-bind="attrs" v-on="on" color="#1b4f72"
                    >mdi-reload</v-icon
                  >
              </template>
              <span>There's an error reaching your master node, Please press if you want to redeploy the master</span>
            </v-tooltip>
      </template>
    </v-data-table>

    <template
      v-if="isVDCAutoscalable"
    >
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
      api="deleteWorkerWorkload"
      title="Delete Worker"
      :messages="deletionMessages"
      :wid="selectedworker"
      :releasestodelete="releasesToDelete"
      @reload-vdcinfo="reloadVdcInfo"
    ></cancel-workload>
    <redeploy-master
      v-model="dialogs.redeployMaster"
      :wid="selectedworker"
      @done="reloadVdcInfo"
    ></redeploy-master>
    <download-kubeconfig v-model="dialogs.downloadKube"></download-kubeconfig>
  </div>
</template>

<script>
module.exports = {
  components: {
    "solution-info": httpVueLoader("../base/Info.vue"),
    "cancel-workload": httpVueLoader("./DeleteConfirmation.vue"),
    "download-kubeconfig": httpVueLoader("./DownloadKubeconfig.vue"),
    "redeploy-master": httpVueLoader("./RedeployMaster.vue"),
  },
  props: ["vdc", "loading"],

  data() {
    return {
      selected: null,
      selectedworker: null,
      tableLoading: false,
      dialogs: {
        info: false,
        cancelWorkload: false,
        downloadKube: false,
        redeployMaster: false,
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
      deletionMessages: {
        confirmationMsg: "Are you sure you want to delete this worker?",
        warningMsg: "",
        successMsg: "Worker deleted successfully",
      },
      releasesToDelete: null,
      isVDCAutoscalable: false,
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
      this.tableLoading = true;
      this.deletionMessages.warningMsg = "";
      this.$api.solutions.checkBeforeDeleteWorkerWorkload(wid)
        .then((response) => {
          this.releasesToDelete = response.data.releases_to_delete;
          releasesString = "<br>"
          timeWarning = "<br> This operation may take time, to safely delete your worker"
          for (release in this.releasesToDelete){
            releasesString += "- " + this.releasesToDelete[release] + "<br>"
          }
          if (this.releasesToDelete.length > 0) {
            this.deletionMessages.warningMsg = "The following release/s will be deleted: " + releasesString + timeWarning;
          }
        }).finally(() => {
          this.tableLoading = false;
          this.dialogs.cancelWorkload = true;
        });
    },

    downloadKubeConfigFile() {
      this.dialogs.downloadKube = true;
    },
    reloadVdcInfo() {
      this.dialogs.cancelWorkload = false;
      this.$emit("reload-vdcinfo", {
        message: "VDC info has been reloaded successfully!",
      });
    },
    downloadThreebotStateFile() {
      this.$api.solutions
        .getThreebotState()
        .then((response) => {
          const blob = new Blob([response.data], {
            type: response.headers["content-type"],
          });
          const url = URL.createObjectURL(blob);
          let filename = response.headers["content-disposition"]
            .split('filename="')[1]
            .slice(0, -1);
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", filename);
          link.click();
          URL.revokeObjectURL(link.href);
        })
        .catch((err) => {
          console.log("Failed to download threebot state due to " + err);
        });
    },
    redeployMaster(wid) {
      this.selectedworker = wid;
      this.dialogs.redeployMaster = true;
    },
  },
  computed: {
    checkMasterExistence() {
      let result = false;
      if (this.vdc) {
        this.vdc.kubernetes.forEach((node) => {
          if (node.role === "master") {
            result = true;
          }
        });
      }
      return result;
    },
    kubernetesData() {
      if (this.vdc) {
        return this.vdc.kubernetes;
      }
    },
  },
  mounted() {
    this.$api.vdc.checkVdcPlanAutoscalable().then((response) => {
      this.isVDCAutoscalable = response.data.autoscalable;
    }).catch((err)=>{
      this.alert(err.message, "error")
    });
  }
};
</script>

<style scoped>
h1 {
  color: #1b4f72;
}
</style>
