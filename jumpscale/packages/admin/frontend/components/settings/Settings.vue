<template>
  <div>
    <base-component title="Settings" icon="mdi-tune">
      <template #actions></template>

      <template #default>
        <v-row align="start" justify="start">
          <v-col class="mt-0 pt-0" cols="12" md="4">
            <base-section title="Admins" icon="mdi-account-lock" :loading="loading.admins">
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
              >{{ admin }}</v-chip>
            </base-section>
          </v-col>
          <v-col class="mt-0 pt-0" cols="12" md="4">
            <base-section
              title="Identities"
              icon="mdi-account-multiple"
              :loading="loading.identities"
            >
              <template #actions>
                <v-btn text @click.stop="dialogs.addIdentity = true">
                  <v-icon left>mdi-plus</v-icon>New
                </v-btn>
              </template>
              <v-chip
                class="mr-2 mb-2"
                @change="setIdentity"
                outlined
                v-for="(identity, i) in identities"
                :key="i"
                :color="getColor(identity.instance_name)"
                @click="openIdentity(identity.instance_name)"
              >{{identity.instance_name}}</v-chip>
            </base-section>
          </v-col>
          <v-col class="mt-0 pt-0" cols="12" md="3">
            <base-section
              class="ma-0 pa-0"
              title="Developer options"
              icon="mdi-settings"
              :loading="loading.developerOptions"
            >
              <v-switch
                hide-details
                class="my-2 pl-2"
                v-model="testCert"
                :label="`Allow staging ssl certificate`"
                @click.stop="setDeveloperOptions()"
              ></v-switch>
              <v-switch
                hide-details
                class="my-2 pl-2"
                v-model="overProvision"
                :label="`Allow over provisioning`"
                @click.stop="setDeveloperOptions()"
              ></v-switch>
              <v-btn
                hide-details
                class="my-2 ml-2"
                small
                color="success"
                @click="clearBlockedNodes()"
              >Clear blocked nodes</v-btn>
            </base-section>
          </v-col>
        </v-row>
      </template>
    </base-component>

    <add-admin v-model="dialogs.addAdmin" @done="listAdmins"></add-admin>
    <remove-admin v-model="dialogs.removeAdmin" :name="selectedAdmin" @done="listAdmins"></remove-admin>
    <identity-info v-model="dialogs.identityInfo" :name="selectedIdentity" @done="listIdentities"></identity-info>
    <add-identity v-model="dialogs.addIdentity" @done="listIdentities"></add-identity>
  </div>
</template>

<script>
module.exports = {
  components: {
    "add-admin": httpVueLoader("./AddAdmin.vue"),
    "remove-admin": httpVueLoader("./RemoveAdmin.vue"),
    "identity-info": httpVueLoader("./IdentityInfo.vue"),
    "add-identity": httpVueLoader("./AddIdentity.vue"),
  },
  data() {
    return {
      loading: {
        admins: false,
        identities: false,
        developerOptions: false,
      },
      selectedAdmin: null,
      dialogs: {
        addAdmin: false,
        removeAdmin: false,
        identityInfo: false,
        addIdentity: false,
      },
      admins: [],
      identity: null,
      selectedIdentity: null,
      identities: [],
      testCert: false,
      overProvision: false,
    };
  },
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
        });
    },
    removeAdmin(name) {
      this.selectedAdmin = name;
      this.dialogs.removeAdmin = true;
    },
    listIdentities() {
      this.getCurrentIdentity();
      this.loading.identities = true;
      this.$api.identities
        .list()
        .then((response) => {
          this.identities = JSON.parse(response.data).data;
        })
        .finally(() => {
          this.loading.identities = false;
        });
    },
    openIdentity(identity) {
      this.selectedIdentity = identity;
      this.dialogs.identityInfo = true;
    },
    getCurrentIdentity() {
      this.loading.identities = true;
      this.$api.admins
        .getCurrentUser()
        .then((response) => {
          this.identity = response.username;
        })
        .finally(() => {
          this.loading.identities = false;
        });
    },
    setIdentity(identityInstanceName) {
      this.$api.identities
        .setIdentity(identityInstanceName)
        .then((response) => {
          this.alert("Identity Updated", "success");
        })
        .catch((error) => {
          this.alert("Failed to update identity", "error");
        });
    },
    getColor(identityInstanceName) {
      if (identityInstanceName == this.identity) {
        return "primary";
      } else {
        return "";
      }
    },
    getDeveloperOptions() {
      this.loading.developerOptions = true;
      this.$api.admins
        .getDeveloperOptions()
        .then((response) => {
          let developerOptions = JSON.parse(response.data).data;
          this.testCert = developerOptions["test_cert"];
          this.overProvision = developerOptions["over_provision"];
        })
        .finally(() => {
          this.loading.developerOptions = false;
        });
    },
    setDeveloperOptions() {
      this.$api.admins
        .setDeveloperOptions(this.testCert, this.overProvision)
        .then((response) => {
          this.alert("Developer options updated", "success");
        })
        .catch((error) => {
          this.alert("Failed to update developer options", "error");
        });
    },
    clearBlockedNodes() {
      this.$api.admins
        .clearBlockedNodes()
        .then((response) => {
          this.alert("Blocked nodes been cleared successfully", "success");
        })
        .catch((error) => {
          this.alert("Failed to clear blocked nodes", "error");
        });
    },
  },
  mounted() {
    this.listAdmins();
    this.getCurrentIdentity();
    this.listIdentities();
    this.getDeveloperOptions();
  },
};
</script>
