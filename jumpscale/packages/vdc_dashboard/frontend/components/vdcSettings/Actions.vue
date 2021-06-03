<template>
  <div>
    <base-dialog :title="`${title} Backup`" v-model="dialog" :loading="loading">
      <template #default v-if="title == 'Delete'">
        Deleting <b class="font-weight-black">{{ name }}</b> backup cannot be
        undone. Enter {{ name }} to confirm.
        <v-text-field v-model="confirmName" dense></v-text-field>
      </template>

      <template #default v-else-if="title == 'Create'">
        Please enter backup name to confirm.
        <v-text-field v-model="confirmName" dense></v-text-field>
        <v-alert dense outlined type="error" v-if="disableSubmit && errorMsg">
          {{errorMsg}}
        </v-alert>
      </template>
      <template #actions>
        <v-btn text @click="close">Cancel</v-btn>
        <v-btn
          text
          color="error"
          @click="del"
          v-if="title == 'Delete'"
          :disabled="disableSubmit"
          >Confirm</v-btn
        >
        <v-btn
          text
          color="error"
          @click="create"
          v-else
          :disabled="disableSubmit"
          >Confirm</v-btn
        >
      </template>
    </base-dialog>
    <popup v-if="show" :msg="msg"></popup>
  </div>
</template>

<script>
module.exports = {
  computed: {
    disableSubmit() {
      if (this.title == "Delete" && this.confirmName === this.name.toString()) {
        return false;
      } else if (this.title == "Create" && this.verifyBackupName(this.confirmName)) {
        return false;
      }
      return true;
    },
  },
  data() {
    return {
      confirmName: null,
      show: false,
      msg: null,
    };
  },
  mixins: [dialog],
  props: ["name", "title", "vdcbackup", "configbackup","backups"],
  methods: {
    del() {
      this.loading = true;
      return this.$api.backup
        .delete(this.vdcbackup, this.configbackup)
        .then((response) => {
          this.show = true;
          this.msg = response.data;
          this.close();
          this.getlist(5000);
        })
        .finally(() => {
          this.loading = false;
          this.confirmName = null;
        });
    },
    create() {
      this.loading = true;
      return this.$api.backup
        .create(this.confirmName)
        .then((response) => {
          this.show = true;
          this.msg = response.data;
          this.close();
          this.getlist(10000);
        })
        .finally(() => {
          this.loading = false;
          this.confirmName = null;
        });
    },
    getlist(timeout=2000) {
      this.$emit("reload-backups", timeout, { message: "Backup list reloaded!" });
    },
    verifyBackupName(backupName){
      currentBackupsName = this.backups.map(item => item.name)
      if (!backupName) {
        this.errorMsg = ""
        return false
      }else if (currentBackupsName.includes(backupName)){
        this.errorMsg = "Can't use the same name twice, Please use another name"
        return false
      }else if (backupName.match('^[a-z0-9]*$') == null) {
        this.errorMsg = "Numbers and small letters only allowed"
        return false
      }else{
        return true
      }
    }
  },
  mounted() {
    this.show = false;
  },
};
</script>
