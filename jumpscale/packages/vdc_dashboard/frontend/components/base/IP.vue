<template>
  <div>
    <div class="actions mb-3">
      <h1 class="d-inline" color="primary" text>{{ $route.name }}</h1>
      <v-btn class="float-right p-4" color="primary" text>
        <v-icon left>mdi-plus</v-icon>Add IP
      </v-btn>
    </div>

    <v-data-table
      :loading="loading"
      :headers="headers"
      :items="ipsData"
      class="elevation-1"
    >
      <template slot="no-data">No VDC instances available</template>
      <template v-slot:item.id="{ item }">
        <div>{{ item.id }}</div>
      </template>

      <template v-slot:item.ip="{ item }">
        <div>{{ item.ip }}</div>
      </template>

      <template v-slot:item.farm="{ item }">
        <div>{{ item.farm }}</div>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-tooltip top>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="deleteIP(item)">
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
    <solution-info
      v-if="selected"
      v-model="dialogs.info"
      :data="selected"
    ></solution-info>
  </div>
</template>

<script>
module.exports = {
  name: "IP",
  components: {
    "solution-info": httpVueLoader("../solutions/Info.vue"),
    "cancel-workload": httpVueLoader("../solutions/Delete.vue"),
  },
  data() {
    return {
      selected: null,
      dialogs: {
        info: false,
        cancelWorkload: false,
      },
      headers: [
        { text: "ID", value: "id" },
        { text: "IP Address", value: "ip" },
        { text: "Farm", value: "farm" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      loading: false,
    };
  },
  methods: {
    open(record) {
      this.selected = record;
      this.dialogs.info = true;
    },
    deleteIP(record) {
      this.selected = record;
      this.dialogs.cancelWorkload = true;
    },
  },
  computed: {
    ipsData() {
      return this.vdc.ips;
    },
  },
};
</script>

<style scoped>
h1 {
  color: #1b4f72;
}
</style>
