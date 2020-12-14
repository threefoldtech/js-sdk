<template>
  <div>
    <div class="actions mb-3">
      <h1 class="d-inline" color="primary" text>{{ $route.name }}</h1>

      <v-btn
        v-if="S3URL"
        class="float-right p-4"
        text
        :href="`https://${S3URL}`"
      >
        <v-icon color="primary" class="mr-2" left>mdi-web</v-icon>S3 Browser
      </v-btn>
    </div>

    <v-data-table :headers="headers" :items="zdbs" class="elevation-1">
      <template slot="no-data">No VDC instances available</template>
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
            <v-btn icon @click.stop="deleteNode(item)">
              <v-icon v-bind="attrs" v-on="on" color="#810000"
                >mdi-delete</v-icon
              >
            </v-btn>
          </template>
          <span>Destroy</span>
        </v-tooltip>
      </template>
    </v-data-table>
    <cancel-workload
      v-if="selected"
      v-model="dialogs.cancelWorkload"
      :data="selected"
    ></cancel-workload>
  </div>
</template>


<script>
module.exports = {
  name: "S3",
  components: {
    "cancel-workload": httpVueLoader("../solutions/Delete.vue"),
  },
  props: ["vdc"],
  data() {
    return {
      dialogs: {
        cancelWorkload: false,
      },
      selected: null,
      headers: [
        { text: "WID", value: "wid" },
        { text: "Node", value: "node" },
        { text: "Disk Size", value: "size" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      S3URL: null,
    };
  },
  methods: {
    deleteNode(record) {
      this.selected = record;
      this.dialogs.cancelWorkload = true;
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
