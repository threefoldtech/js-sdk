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
        @click:close="removeAdmin(admin)"
        outlined
        label
        close
        close-icon="mdi-close-circle-outline"
        >{{ admin }}</v-chip
      >
    </base-section>
  </div>
</template>
<script>
module.exports = {
  components: {},
  data() {
    return {
      admins: [],
    };
  },
  props: ["vdc", "loading"],
  methods: {
    listAdmins() {
      this.loading.admins = true;
      this.$api.admins
        .list()
        .then((response) => {
          this.admins = JSON.parse(response.data).data;
        })
        .finally(() => {
          this.loading.admins = false;
          console.log("admins", this.admins);
        });
    },
  },
  mounted() {
    this.listAdmins();
  },
};
</script>
