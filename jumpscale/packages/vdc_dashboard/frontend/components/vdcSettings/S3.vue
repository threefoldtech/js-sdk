<template>
  <div>
    <div class="actions mb-3">
      <h1 class="d-inline" color="primary" text>Storage Containers</h1>
      <v-btn
        class="float-right p-4"
        color="primary"
        text
        @click.stop="(dialogs.downloadInfo = true), (downloadType = 'zstor6')"
      >
        <v-icon left>mdi-download</v-icon>Z-STOR Config (IPv6)
      </v-btn>
      <v-btn
        class="float-right p-4"
        color="primary"
        text
        @click.stop="(dialogs.downloadInfo = true), (downloadType = 'zstor4')"
      >
        <v-icon left>mdi-download</v-icon>Z-STOR Config (IPv4)
      </v-btn>
      <v-btn
        class="float-right p-4"
        color="primary"
        text
        @click.stop="(dialogs.downloadInfo = true), (downloadType = 'zdbs')"
      >
        <v-icon left>mdi-download</v-icon>Zdbs Info
      </v-btn>
      <v-btn
        class="float-right p-4"
        color="primary"
        text
        @click.stop="enableQuantumStorage"
      >
        <v-icon left>mdi-folder-key-network</v-icon>Quantum Storage
        Configurations
      </v-btn>
      <v-btn
        v-if="S3URL"
        class="float-right p-4"
        text
        :href="`https://${S3URL}`"
      >
        <v-icon color="primary" class="mr-2" left>mdi-web</v-icon>Storage
        Browser
      </v-btn>
      <v-btn
        class="float-right p-4"
        color="primary"
        text
        @click.stop="openChatflow('extend_storage')"
      >
        <v-icon left>mdi-plus</v-icon>Add node
      </v-btn>
    </div>
    <v-data-table
      :headers="headers"
      :loading="loading || tableloading"
      :items="zdbs()"
      class="elevation-1"
    >
      <template slot="no-data">No VDC instance available</template>
      <template v-slot:item.wid="{ item }">
        <div>{{ item.wid }}</div>
      </template>

      <template v-slot:item.node="{ item }">
        <div>{{ item.node_id }}</div>
      </template>

      <template v-slot:item.size="{ item }">
        <div>{{ item.size }} GB</div>
      </template>

      <template v-slot:item.actions="{ item }">
        <v-tooltip top>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="deleteZdb(item.wid)">
              <v-icon v-bind="attrs" v-on="on" color="#810000"
                >mdi-delete</v-icon
              >
            </v-btn>
          </template>
          <span>Delete</span>
        </v-tooltip>
      </template>
    </v-data-table>
    <base-dialog
      title="Download storage containers Information file"
      v-model="dialogs.downloadInfo"
      v-if="dialogs.downloadInfo"
    >
      <template #default>
        <p v-if="downloadType === 'zdbs'">
          WARNING: Please keep the storage containers Information safe and
          secure.
        </p>
        <p v-else-if="downloadType === 'zstor'">
          WARNING: You should update the TOML file with your custom
          configurations as documented
          <a
            href="https://github.com/threefoldtech/0-stor_v2#config-file"
            target="blank"
            >here</a
          >.
        </p>
      </template>
      <template #actions>
        <v-btn text color="error" @click="downloadFile()">Download</v-btn>
      </template>
    </base-dialog>
    <enable-quantumstorage
      v-model="dialogs.enableQuantum"
    ></enable-quantumstorage>
    <cancel-zdb
      v-if="selectedZdb"
      v-model="dialogs.cancelZdb"
      api="deleteZdb"
      title="Delete ZDB"
      :messages="deletionMessages"
      :wid="selectedZdb"
      @reload-vdcinfo="reloadVdcInfo"
    ></cancel-zdb>
  </div>
</template>

<script>
module.exports = {
  props: ["vdc", "tableloading"],
  mixins: [dialog],
  components: {
    "cancel-zdb": httpVueLoader("./DeleteConfirmation.vue"),
    "enable-quantumstorage": httpVueLoader("./QuantumStorage.vue"),
  },
  data() {
    return {
      selected: null,
      selectedZdb: null,
      headers: [
        { text: "WID", value: "wid" },
        { text: "Node", value: "node" },
        { text: "Disk Size", value: "size" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      S3URL: null,
      downloadType: null,
      dialogs: {
        downloadInfo: false,
        enableQuantum: false,
        cancelZdb: false,
      },
      deletionMessages: {
        confirmationMsg: "Are you sure you want to delete the zdb?",
        successMsg: "ZDB deleted successfully",
      },
    };
  },
  methods: {
    downloadFile() {
      let data = null;
      let fileType = null;
      if (this.downloadType === "zdbs") {
        fileType = "json";
        this.loading = true;
        this.$api.solutions
          .getZdbSecret()
          .then((response) => {
            Secret = response.data.data;
            let zdbs = this.vdc.s3.zdbs;
            for (i in this.vdc.s3.zdbs) {
              let zdb = this.vdc.s3.zdbs[i];
              zdb.password = Secret;
            }
            data = JSON.stringify(zdbs, null, "\t");
            const blob = new Blob([data]);
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.setAttribute(
              "download",
              `${this.vdc.vdc_name}ZDBsInfo.${fileType}`
            );
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            this.dialogs.downloadInfo = false;
          })
          .finally(() => {
            this.loading = false;
          });
      } else if (this.downloadType === "zstor6") {
        fileType = "toml";
        this.loading = true;
        this.$api.solutions
          .getZstorConfig(6)
          .then((response) => {
            data = response.data.data;
            const blob = new Blob([data]);
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.setAttribute(
              "download",
              `${this.vdc.vdc_name}ZDBsInfo.${fileType}`
            );
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            this.dialogs.downloadInfo = false;
          })
          .finally(() => {
            this.loading = false;
          });
      } else if (this.downloadType === "zstor4") {
        fileType = "toml";
        this.loading = true;
        this.$api.solutions
          .getZstorConfig(4)
          .then((response) => {
            data = response.data.data;
            const blob = new Blob([data]);
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.setAttribute(
              "download",
              `${this.vdc.vdc_name}ZDBsInfo.${fileType}`
            );
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            this.dialogs.downloadInfo = false;
          })
          .finally(() => {
            this.loading = false;
          });
      }
    },
    enableQuantumStorage() {
      this.dialogs.enableQuantum = true;
    },
    deleteZdb(wid) {
      this.selectedZdb = wid;
      this.dialogs.cancelZdb = true;
    },
    reloadVdcInfo() {
      this.dialogs.cancelZdb = false;
      this.$emit("reload-vdcinfo", {
        message: "VDC info has been reloaded successfully!",
      });
    },

    openChatflow(topic) {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: topic },
      });
    },
    // Switched to method way as it updating whenever component updated
    zdbs() {
      if (this.vdc) {
        this.S3URL = this.vdc.s3.domain;
        return this.vdc.s3.zdbs;
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
