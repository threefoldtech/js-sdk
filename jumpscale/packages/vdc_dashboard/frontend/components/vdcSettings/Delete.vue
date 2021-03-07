<template>
  <div>
    <base-dialog
      title="Delete Backup"
      v-model="dialog"
      :error="error"
      :loading="loading"
    >
      <template #default>
        Are you sure you want to delete backup, this action can't be undone?
        Please type <b class="font-weight-black">{{ name }}</b> to confirm.
        <v-text-field v-model="confirmName" dense></v-text-field>
      </template>
      <template #actions>
        <v-btn text @click="close">Close</v-btn>
        <v-btn text color="error" @click="submit" :disabled="disableSubmit"
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
      if (this.confirmName === this.name.toString()) {
        return false;
      }
      return true;
    },
  },
  data() {
    return {
      confirmName: "",
      show: false,
      msg: null,
    };
  },
  mixins: [dialog],
  props: ["name"],
  methods: {
    submit() {
      this.loading = true;
      return this.$api.backup
        .delete(this.name)
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
  },
  mounted() {
    this.show = false;
  },
};
</script>
