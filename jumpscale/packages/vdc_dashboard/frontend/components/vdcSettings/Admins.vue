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
