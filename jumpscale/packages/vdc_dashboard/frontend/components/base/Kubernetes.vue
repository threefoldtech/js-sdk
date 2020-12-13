<template>
  <div>
    <div class="actions mb-3">
      <h1 class="d-inline" color="primary" text>{{ $route.name }}</h1>
      <v-btn class="float-right p-4" color="primary" text @click.stop='openChatflow("add_k3s_node")'>
        <v-icon left>mdi-plus</v-icon>Add node
      </v-btn>
    </div>

    <v-data-table
      :headers="headers"
      :items="kubernetesData"
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

      <template v-slot:item.size="{ item }">
        <div>{{ item.size }} GB</div>
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
    <solution-info
      v-if="selected"
      v-model="dialogs.info"
      :data="selected"
    ></solution-info>
    <cancel-workload
      v-if="selected"
      v-model="dialogs.cancelWorkload"
      :data="selected"
    ></cancel-workload>
  </div>
</template>

<script>
module.exports = {
  name: "Kubernetes",
  components: {
    "solution-info": httpVueLoader("../solutions/Info.vue"),
    "cancel-workload": httpVueLoader("../solutions/Delete.vue"),
  },
  props: ["vdc"],

  data() {
    return {
      selected: null,
      dialogs: {
        info: false,
        cancelWorkload: false,
      },
      headers: [
        { text: "WID", value: "wid" },
        { text: "IP Address", value: "ip" },
        { text: "Role", value: "role" },
        { text: "Disk Size", value: "size" },
        { text: "Actions", value: "actions", sortable: false },
      ],
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
    deleteNode(record) {
      this.selected = record;
      this.dialogs.cancelWorkload = true;
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
