<template>
  <div>
    <base-dialog :title="`Restore ${name}`" v-model="dialog" :loading="loading">
      <template #default>
        WARNING: It will restore the system to the state of the backup, any
        unsaved changes will be lost Are you sure to continue?
      </template>
      <template #actions>
        <v-btn text @click="close">Cancel</v-btn>
        <v-btn text @click="restore" color="error">Continue</v-btn>
      </template>
    </base-dialog>
    <popup v-if="show" :msg="msg"></popup>
  </div>
</template>

<script>
module.exports = {
  data() {
    return {
      show: false,
      msg: null,
    };
  },
  props: ["name", "vdcbackup", "configbackup"],
  mixins: [dialog],
  methods: {
    restore() {
      this.loading = true;
      this.$api.backup
        .restore(this.vdcbackup, this.configbackup)
        .then((response) => {
          this.show = true;
          this.msg = response.data;
          this.close();
          this.getlist();
        })
        .finally(() => {
          this.loading = false;
        });
    },
    close() {
      this.dialog = false;
    },
    getlist() {
      this.$emit("reload-backups", { message: "Backup list reloaded!" });
    },
  },
  mounted() {
    this.show = false;
  },
};
</script>
