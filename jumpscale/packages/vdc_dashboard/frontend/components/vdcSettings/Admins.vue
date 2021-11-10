<template>
  <div>
    <!-- List-Admins -->
    <base-section
      title="Admins"
      icon="mdi-account-lock"
      :loading="loading.admins"
    >
      <template #actions>
        <v-btn text @click.stop="dialogs.addAdmin = true">
          <v-icon left>mdi-plus</v-icon>Add
        </v-btn>
      </template>

      <v-chip
        class="ma-2"
        color="primary"
        min-width="50"
        v-for="admin in admins"
        :key="admin"
        @click:close="isLastAdmin() ? undefined : removeAdmin(admin)"
        outlined
        label
        :close="!isLastAdmin()"
        :close-icon="isLastAdmin() ? undefined : 'mdi-close-circle-outline'"
        >{{ admin }}</v-chip
      >
    </base-section>
    <add-admin v-model="dialogs.addAdmin" @done="listAdmins"></add-admin>
    <remove-admin
      v-model="dialogs.removeAdmin"
      :name="selectedAdmin"
      @done="listAdmins"
    ></remove-admin>
  </div>
</template>
<script>
module.exports = {
  components: {
    "add-admin": httpVueLoader("./admin_settings/AddAdmin.vue"),
    "remove-admin": httpVueLoader("./admin_settings/RemoveAdmin.vue"),
  },
  data() {
    return {
      admins: [],
      selectedAdmin: null,
      dialogs: {
        addAdmin: false,
        removeAdmin: false,
      },
    };
  },
  props: ["vdc", "loading"],
  methods: {
    listAdmins() {
      this.loading.admins = true;
      this.$api.admins
        .list()
        .then((response) => {
          this.admins = response.data.data;
        })
        .finally(() => {
          this.loading.admins = false;
        });
    },
    removeAdmin(name) {
      this.selectedAdmin = name;
      this.dialogs.removeAdmin = true;
    },
    isLastAdmin() {
      return this.admins.length === 1;
    },
  },
  mounted() {
    this.listAdmins();
  },
};
</script>
