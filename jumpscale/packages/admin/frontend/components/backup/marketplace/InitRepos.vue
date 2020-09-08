<template>
  <base-dialog title="Init repo" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      <v-form>
        <v-text-field v-model="form.password" type="password" label="password" dense></v-text-field>
      </v-form>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text @click="submit">Confirm</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  mixins: [dialog],

  methods: {
    submit() {
      this.loading = true;
      this.error = null;
      this.$api.mrktbackup
        .init(this.form.password)
        .then(response => {
          console.log(this.form)
          this.done("repos is inited");
          location.reload();
        })
        .catch(error => {
          this.error = `${error.message}. Backup service is only available through online deployed 3Bots`;
        })
        .finally(() => {
          this.loading = false;
        });
    }
  }
};
</script>
