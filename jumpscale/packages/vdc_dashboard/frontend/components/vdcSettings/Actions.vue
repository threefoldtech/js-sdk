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
      } else if (this.title == "Create" && this.confirmName) {
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
  props: ["name", "title", "vdcbackup", "configbackup"],
  methods: {
    del() {
      this.loading = true;
      return this.$api.backup
        .delete(this.vdcbackup, this.configbackup)
        .then((response) => {
          this.show = true;
          this.msg = response.data;
          this.close();
          this.getlist();
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
  },
  mounted() {
    this.show = false;
  },
};
</script>
