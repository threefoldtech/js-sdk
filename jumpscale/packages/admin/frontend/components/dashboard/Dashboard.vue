<template>
  <div>
    <base-component title="Dashboard" icon="mdi-view-dashboard" :loading="loading">

      <template #actions>

        <v-btn color="primary" text @click.stop="dialogs.addAdmin = true">
          <v-icon left>mdi-account-plus-outline</v-icon> Add Admin
        </v-btn>

        <v-btn color="primary" text @click.stop="dialogs.installPackage = true">
          <v-icon left>mdi-package-variant-closed</v-icon> New Package
        </v-btn>

        <v-btn color="primary" text to="/settings">
          <v-icon left>mdi-tune</v-icon> Settings
        </v-btn>
      </template>


      <template #default>
            <v-row>
                <v-col><health-checks></health-checks><wikis></wikis><memory-usage></memory-usage>
                <disk-usage></disk-usage></v-col>
                <v-col><processes></processes></v-col>
            </v-row>
      </template>
    </base-component>

    <add-admin v-model="dialogs.addAdmin"></add-admin>
    <add-package v-model="dialogs.installPackage"></add-package>
    <create-wallet v-model="dialogs.createWallet"></create-wallet>

  </div>

</template>
<script>
  module.exports = {
    components: {
      'add-admin': httpVueLoader("../settings/AddAdmin.vue"),
      'add-package': httpVueLoader("../packages/Add.vue"),
      'create-wallet': httpVueLoader("../wallets/Create.vue"),
      'memory-usage': httpVueLoader("./MemoryUsage.vue"),
      'disk-usage': httpVueLoader("./DiskUsage.vue"),
      'health-checks': httpVueLoader("./HealthChecks.vue"),
      'processes': httpVueLoader("./Processes.vue"),
      'wikis': httpVueLoader("./Wikis.vue"),
      'system': httpVueLoader("./System.vue")
    },
    data () {
      return {
        loading: false,
        dialogs: {
          addAdmin: false,
          installPackage: false,
          createWallet: false
        }
      }
    }
  }
</script>

<style scoped>
.row, .col {
  padding-top: 0px !important;
  margin-top: 0px !important;
}
</style>
