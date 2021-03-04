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
    <!-- :loading="loading" -->

    <v-data-table :headers="headers" :items="backups" class="elevation-1">
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
  props: ["vdc"],

  data() {
    return {
      selected: null,
      selectedworker: null,
      dialogs: {
        info: false,
        cancelWorkload: false,
        downloadKube: false,
      },
      backups: [],
      headers: [
        { text: "Name", value: "name" },
        { text: "Start Date", value: "start_timestamp" },
        { text: "Expiry Date", value: "expiration" },
        { text: "Status", value: "status" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      backup_data: [
        {
          name: "config-20210301101042",
          expiration: 1617185447,
          status: "Completed",
          start_timestamp: 1614593447,
          completion_timestamp: 1614593448,
          errors: 0,
          progress: {
            totalItems: 52,
            itemsBackedUp: 52,
          },
        },
        {
          name: "vdc-20210301101042",
          expiration: 1617185442,
          status: "PartiallyFailed",
          start_timestamp: 1614593442,
          completion_timestamp: 1614593446,
          errors: 3,
          progress: {
            totalItems: 15,
            itemsBackedUp: 15,
          },
        },
        {
          name: "config-20210301090945",
          expiration: 1617181788,
          status: "Completed",
          start_timestamp: 1614589788,
          completion_timestamp: 1614589789,
          errors: 0,
          progress: {
            totalItems: 49,
            itemsBackedUp: 49,
          },
        },
        {
          name: "vdc-20210301104328",
          expiration: 1617187408,
          status: "PartiallyFailed",
          start_timestamp: 1614595408,
          completion_timestamp: 1614595412,
          errors: 3,
          progress: {
            totalItems: 10,
            itemsBackedUp: 10,
          },
        },
        {
          name: "config-20210301104329",
          expiration: 1617187413,
          status: "Completed",
          start_timestamp: 1614595413,
          completion_timestamp: 1614595414,
          errors: 0,
          progress: {
            totalItems: 54,
            itemsBackedUp: 54,
          },
        },
        {
          name: "vdc-20210301114425",
          expiration: 1617191065,
          status: "PartiallyFailed",
          start_timestamp: 1614599065,
          completion_timestamp: 1614599068,
          errors: 3,
          progress: {
            totalItems: 12,
            itemsBackedUp: 12,
          },
        },
        {
          name: "config-20210301114425",
          expiration: 1617191069,
          status: "Completed",
          start_timestamp: 1614599069,
          completion_timestamp: 1614599070,
          errors: 0,
          progress: {
            totalItems: 55,
            itemsBackedUp: 55,
          },
        },
        {
          name: "config-20210301124425",
          expiration: 1617194669,
          status: "Completed",
          start_timestamp: 1614602669,
          completion_timestamp: 1614602670,
          errors: 0,
          progress: {
            totalItems: 55,
            itemsBackedUp: 55,
          },
        },
      ],
    };
  },
  methods: {
    createBackup() {
      this.$api.backup
        .create()
        .then((response) => {
          // console.log(response.data);
        })
        .finally(() => {
          console.log("Backup created");
        });
    },
    list() {
      this.$api.backup
        .list()
        .then((response) => {
          //   backups = response.data;
        })
        .finally(() => {
          console.log("Data listed");
          this.backups = this.backup_data;
        });
    },
    restore(name) {
      this.$api.backup
        .restore(name)
        .then((response) => {
          //   backups = response.data;
          this.list();
        })
        .finally(() => {
          console.log("Backup Restored");
          this.backups = this.backup_data;
        });
    },
    open(record) {
      this.selected = record;
      this.dialogs.info = true;
    },
    deleteBackup(name) {
      this.selectedworker = name;
      this.dialogs.cancelWorkload = true;
      this.$api.backup
        .delete(name)
        .then((response) => {
          //   backups = response.data;
          this.list();
        })
        .finally(() => {
          console.log("Backup Deleted");
        });
    },
    timeDifference(ts) {
      var timestamp = moment.unix(ts);
      var now = new Date();
      return timestamp.to(now);
    },
    getStatus(status) {
      if (status == "PartiallyFailed") return "red";
      else if (status == "Completed") return "green";
      else return "orange";
    },
  },
  computed: {
    backupData() {
      if (this.vdc) {
        return this.vdc.backup;
      }
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
