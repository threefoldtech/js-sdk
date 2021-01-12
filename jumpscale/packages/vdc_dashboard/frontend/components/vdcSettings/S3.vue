<template>
  <div>
    <div class="actions mb-3">
      <h1 class="d-inline" color="primary" text>Storage Nodes</h1>
      <v-btn
        class="float-right p-4"
        color="primary"
        text
        @click.stop="(dialogs.downloadInfo = true), (downloadType = 'zstor')"
      >
        <v-icon left>mdi-download</v-icon>Z-STOR Config
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
        v-if="S3URL"
        class="float-right p-4"
        text
        :href="`https://${S3URL}`"
      >
        <v-icon color="primary" class="mr-2" left>mdi-web</v-icon>Storage
        Browser
      </v-btn>
    </div>
    <v-data-table
      :headers="headers"
      :loading="loading"
      :items="zdbs"
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
    </v-data-table>
    <base-dialog
      title="Download storage nodes Information file"
      v-model="dialogs.downloadInfo"
      v-if="dialogs.downloadInfo"
    >
      <template #default>
        <p v-if="downloadType === 'zdbs'">
          WARINING: Please keep the storage nodes Information safe and secure.
        </p>
        <p v-else-if="downloadType === 'zstor'">
          WARINING: You should update the TOML file with your custom
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
  </div>
</template>


<script>
module.exports = {
  props: ["vdc"],
  mixins: [dialog],
  data() {
    return {
      selected: null,
      headers: [
        { text: "WID", value: "wid" },
        { text: "Node", value: "node" },
        { text: "Disk Size", value: "size" },
      ],
      S3URL: null,
      downloadType: null,
      dialogs: {
        downloadInfo: false,
      },
    };
  },
  methods: {
    downloadFile() {
      let data = null;
      let fileType = null;
      if (this.downloadType === "zdbs") {
        fileType = "json";
        data = JSON.stringify(this.vdc.s3.zdbs, null, "\t");
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
      } else if (this.downloadType === "zstor") {
        fileType = "toml";
        data = {
          data_shards: 2,
          parity_shards: 1,
          redundant_groups: 0,
          redundant_nodes: 0,
          encryption: {
            algorithm: "AES",
            key: "",
          },
          compression: {
            algorithm: "snappy",
          },
          groups: [],
        };
        for (i in this.vdc.s3.zdbs) {
          let zdb = this.vdc.s3.zdbs[i];
          data.groups.push({
            backends: [
              {
                address: `[${zdb.ip_address}]:${zdb.port}`,
                namespace: zdb.namespace,
              },
            ],
          });
        }
        this.loading = true;
        this.$api.solutions
          .getZstorConfig(data)
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
  },
  computed: {
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
