<template>
  <div>
    <base-dialog :title="`${title} Backup`" v-model="dialog" :loading="loading">
      <template #default v-if="title == 'Delete'">
        Are you sure you want to {{ title }} backup, this action can't be
        undone? Please type <b class="font-weight-black">{{ name }}</b> to
        confirm.
        <v-text-field v-model="confirmName" dense></v-text-field>
      </template>

      <template #default v-else-if="title == 'Create'">
        Are you sure you want to {{ title }} backup, this action can't be
        undone? Please enter backup name to confirm.
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
  props: ["name", "title"],
  methods: {
    del() {
      this.loading = true;
      return this.$api.backup
        .delete(this.name)
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
          this.getlist();
        })
        .finally(() => {
          this.loading = false;
          this.confirmName = null;
        });
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
