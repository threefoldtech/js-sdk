<template>
  <div>
    <div class="actions mb-3">
      <h1 class="d-inline" color="primary" text>Backup &amp; Restore</h1>
      <v-btn
        class="float-right p-4"
        color="primary"
        text
        @click.stop="createBackup"
      >
        <v-icon left>mdi-plus</v-icon>Create backup
      </v-btn>
    </div>
    <v-data-table
      :loading="loading"
      :headers="headers"
      :items="backups"
      class="elevation-1"
    >
      <template slot="no-data">No VDC instances available</template>
      <template v-slot:item.name="{ item }">
        <div>{{ item.name }}</div>
      </template>

      <template v-slot:item.start_timestamp="{ item }">
        <div>{{ timeDifference(item.start_timestamp) }}</div>
      </template>

      <template v-slot:item.expiration="{ item }">
        <div>{{ timeDifference(item.expiration) }}</div>
      </template>

      <template v-slot:item.status="{ item }">
        <v-chip :color="getStatus(item.status)" dark>{{ item.status }}</v-chip>
      </template>

      <template v-slot:item.actions="{ item }">
        <v-tooltip top>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="restore(item.name)">
              <v-icon v-bind="attrs" v-on="on" color="#206a5d"
                >mdi-backup-restore</v-icon
              >
            </v-btn>
          </template>
          <span>Restore</span>
        </v-tooltip>
        <v-tooltip top>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="open(item)">
              <v-icon v-bind="attrs" v-on="on" color="#1979b5"
                >mdi-information-outline</v-icon
              >
            </v-btn>
          </template>
          <span>Show Information</span>
        </v-tooltip>

        <v-tooltip top v-if="item.role !== 'master'">
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="deleteBackup(item.name)">
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
    <cancel-backup
      v-if="selectedBackup"
      v-model="dialogs.cancelBackup"
      :name="selectedBackup"
    ></cancel-backup>

    <popup v-if="show" :msg="msg"></popup>
  </div>
</template>
<script>
module.exports = {
  components: {
    "solution-info": httpVueLoader("../base/Info.vue"),
    "cancel-backup": httpVueLoader("./Delete.vue"),
  },
  props: ["vdc"],

  data() {
    return {
      selected: null,
      selectedBackup: null,
      dialogs: {
        info: false,
        cancelBackup: false,
      },
      backups: [],
      headers: [
        { text: "Name", value: "name" },
        { text: "Start Date", value: "start_timestamp" },
        { text: "Expiry Date", value: "expiration" },
        { text: "Status", value: "status" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      loading: false,
      show: false,
      msg: null,
    };
  },
  methods: {
    createBackup() {
      this.loading = true;
      this.$api.backup
        .create()
        .then((response) => {
          this.show = true;
          this.msg = response.data;
          this.list();
        })
        .finally(() => {
          this.loading = false;
        });
    },
    list() {
      this.loading = true;
      this.$api.backup
        .list()
        .then((response) => {
          this.backups = response.data.data;
        })
        .finally(() => {
          this.loading = false;
          this.show = false;
        });
    },
    restore(name) {
      this.loading = true;
      this.$api.backup
        .restore(name)
        .then((response) => {
          this.show = true;
          this.msg = response.data;
          this.list();
        })
        .finally(() => {
          this.loading = false;
        });
    },
    open(record) {
      this.selected = record;
      this.dialogs.info = true;
    },
    deleteBackup(name) {
      this.selectedBackup = name;
      this.dialogs.cancelBackup = true;
    },
    timeDifference(ts) {
      var timestamp = moment.unix(ts);
      var now = new Date();
      return timestamp.to(now);
    },
    getStatus(status) {
      if (status == "Error") return "red";
      else if (status == "Completed") return "green";
      else return "orange";
    },
  },
  mounted() {
    this.list();
  },
};
</script>

<style scoped>
h1 {
  color: #1b4f72;
}
</style>
