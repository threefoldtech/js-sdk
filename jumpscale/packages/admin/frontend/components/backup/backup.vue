<template>
  <div>
    <base-component title="Backup" icon="mdi-database" :loading="loading">
      <template #actions>
        <v-btn color="primary" text @click.stop="addDialog = true">
          <v-icon left>mdi-plus</v-icon>Add
        </v-btn>
      </template>

      <template #default></template>
    </base-component>

    <add-package v-model="addDialog" @done="listPackages"></add-package>
    <delete-package v-model="deleteDialog" :name="selected" @done="listPackages"></delete-package>
  </div>
</template>

<script>
module.exports = {
  components: {
    "add-package": httpVueLoader("./Add.vue"),
    "delete-package": httpVueLoader("./Delete.vue")
  },
  data() {
    return {
      loading: false,
      packages: [],
      selected: null,
      addDialog: false,
      deleteDialog: false
    };
  },
  methods: {
    listPackages() {
      this.loading = true;
      this.$api.packages
        .list()
        .then(response => {
          this.packages = JSON.parse(response.data).data;
        })
        .finally(() => {
          this.loading = false;
        });
    }
  },
  mounted() {
    this.listPackages();
  }
};
</script>
