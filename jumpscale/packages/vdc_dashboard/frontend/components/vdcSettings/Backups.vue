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
    <div>
      <v-text-field
        v-model="search"
        label="Search"
        single-line
        hide-details
      ></v-text-field>
    </div>
    <v-data-table
      :loading="loading"
      :headers="headers"
      :items="backups"
      :search="search"
      :sort-by.sync="sortBy"
      class="elevation-1"
    >
      <template slot="no-data">No backups yet</template>
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
        <v-chip :color="getStatus(item.status)" dark>{{
          updateStatus(item.status)
        }}</v-chip>
      </template>

      <template v-slot:item.actions="{ item }">
        <v-tooltip top>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="restore(item.name, item.vdc_backup, item.config_backup)">
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
            <v-btn icon @click.stop="deleteBackup(item.name, item.vdc_backup, item.config_backup)">
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
    <actions
      :title="title"
      v-model="dialogs.actions"
      :name="selectedBackup"
      :vdcbackup="vdcBackupName"
      :configbackup="configBackupName"
      :backups="backups"
      @reload-backups="reload"
    ></actions>
    <restore-backup
      :name="selectedBackup"
      :vdcbackup="vdcBackupName"
      :configbackup="configBackupName"
      v-model="dialogs.restoreBackup"
      @reload-backups="reload"
    ></restore-backup>

    <popup v-if="show" :msg="msg"></popup>
  </div>
</template>
<script>
module.exports = {
  components: {
    "solution-info": httpVueLoader("../base/Info.vue"),
    actions: httpVueLoader("./Actions.vue"),
    "restore-backup": httpVueLoader("./Restore.vue"),
  },
  props: ["vdc"],

  data() {
    return {
      search: "",
      selected: null,
      selectedBackup: null,
      vdcBackupName: null,
      configBackupName: null,
      sortBy: "start_timestamp",
      dialogs: {
        info: false,
        actions: false,
        restoreBackup: false,
      },
      backups: [],
      headers: [
        { text: "Name", value: "name" },
        { text: "Back-up Date", value: "start_timestamp" },
        { text: "Back-up Removal Date", value: "expiration" },
        { text: "Status", value: "status" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      loading: false,
      show: false,
      msg: null,
      title: null,
    };
  },
  methods: {
    createBackup() {
      this.title = "Create";
      this.dialogs.actions = true;
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
    restore(name, vdcBackup, configBackup) {
      this.selectedBackup= name
      this.vdcBackupName = vdcBackup;
      this.configBackupName = configBackup;
      this.dialogs.restoreBackup = true;
    },
    open(record) {
      this.selected = record;
      this.dialogs.info = true;
    },
    deleteBackup(name, vdcBackup, configBackup) {
      this.title = "Delete";
      this.selectedBackup = name;
      this.vdcBackupName = vdcBackup;
      this.configBackupName = configBackup;
      this.dialogs.actions = true;
    },
    timeDifference(ts) {
      var timestamp = new Date(ts * 1000).toLocaleString("en-GB");
      return timestamp;
    },
    getStatus(status) {
      if (status == "Error") return "red";
      else if (status == "Completed") return "green";
      else return "orange";
    },
    confirmCreation() {
      this.dialogs.confirmBackup = true;
    },
    reload(timeout) {
      this.loading = true;
      setTimeout(()=> {this.list()} , timeout);
    },
    updateStatus(status) {
      if (status === "PartiallyFailed") {
        return "Backed up MetadataOnly";
      } else {
        return status;
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

.v-input {
  width: 20%;
  margin-left: auto;
}
</style>
