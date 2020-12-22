<template>
  <div>
    <div class="actions mb-3">
      <h1 class="d-inline" color="primary" text>Storage Nodes</h1>

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
        v-else
        class="float-right p-4"
        :loading="loading"
        text
        @click.stop="exposeS3()"
      >
        <v-icon color="primary" class="mr-2" left>mdi-upload-multiple</v-icon
        >Expose storgae controller
      </v-btn>
    </div>
    <v-data-table :headers="headers" :loading="loading" :items="zdbs" class="elevation-1">
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
  </div>
</template>


<script>
module.exports = {
  props: ["vdc", "loading"],
  data() {
    return {
      selected: null,
      headers: [
        { text: "WID", value: "wid" },
        { text: "Node", value: "node" },
        { text: "Disk Size", value: "size" },
      ],
      S3URL: null,
    };
  },
  methods: {
    exposeS3() {
      this.loading = true;
      this.$api.solutions
        .exposeS3()
        .then((response) => {
          location.reload();
        })
        .catch((error) => {
          console.log(`${error.message}`);
          this.loading = false;
        })
        .finally(() => {
          this.loading = false;
        });
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
