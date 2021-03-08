<template>
  <div>
    <base-dialog :title="`Restore ${name}`" v-model="dialog" :loading="loading">
      <template #default>
        WARINING: It will restore the system to the state of the backup, any
        unsaved changes will be lost Are you sure to continue?
      </template>
      <template #actions>
        <v-btn text @click="close">Cancel</v-btn>
        <v-btn text color="error" @click="restore">Continue</v-btn>
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
  props: ["name"],
  mixins: [dialog],
  methods: {
    restore() {
      this.loading = true;
      this.$api.backup
        .restore(this.name)
        .then((response) => {
          this.show = true;
          this.msg = response.data;
          this.close();
          this.$router.go(0);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    close() {
      this.dialog = false;
    },
  },
  mounted() {
    this.show = false;
  },
};
</script>
