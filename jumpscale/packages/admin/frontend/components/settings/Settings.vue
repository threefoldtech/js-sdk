<template>
  <div>
    <base-component title="Settings" icon="mdi-tune">
      <template #actions></template>

      <template #default>
        <v-row align="start" justify="start">
          <v-col class="mt-0 pt-0" cols="12" md="4">
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
              >{{ admin }}</v-chip>
            </base-section>
            <!-- List-Escalation-Emails -->
            <base-section
              class="mt-3"
              title="Escalation Emails"
              icon="mdi-account-lock"
              :loading="loading.escalationEmails"
            >
              <template #actions>
                <v-btn text @click.stop="dialogs.escalationEmail = true">
                  <v-icon left>mdi-plus</v-icon>Add
                </v-btn>
              </template>

              <v-chip
                class="ma-2"
                color="primary"
                min-width="50"
                v-for="email in escalationEmails"
                :key="email"
                @click:close="removeEscalationEmail(email)"
                outlined
                label
                close
                close-icon="mdi-close-circle-outline"
                >{{ email }}</v-chip
              >
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
              >{{ identity.instance_name }}</v-chip>
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
              <v-switch
                hide-details
                class="my-2 pl-2"
                v-model="explorerLogs"
                :label="`Enable explorer logs`"
                @click.stop="setDeveloperOptions()"
              ></v-switch>
              <v-switch
                hide-details
                class="my-2 pl-2"
                v-model="escalationEmailsEnabled"
                :label="`Enable sending escalation emails`"
                @click.stop="setDeveloperOptions()"
              ></v-switch>
              <v-switch
                hide-details
                class="my-2 pl-2"
                v-model="sortNodesBySru"
                :label="`Sort nodes by SRU`"
                @click.stop="setDeveloperOptions()"
              ></v-switch>
              <v-btn
                hide-details
                class="my-2 ml-2"
                small
                color="info"
                @click="showConfig()"
              >Show 3Bot configurations</v-btn>
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
    <add-escaltion-email
      v-model="dialogs.escalationEmail"
      @done="listEscaltionEmails"
    ></add-escaltion-email>
    <remove-admin
      v-model="dialogs.removeAdmin"
      :name="selectedAdmin"
      @done="listAdmins"
    ></remove-admin>
    <identity-info
      v-model="dialogs.identityInfo"
      :name="selectedIdentity"
      @done="listIdentities"
    ></identity-info>
    <add-identity
      v-model="dialogs.addIdentity"
      @done="listIdentities"
    ></add-identity>
    <config-view v-if="configurations" v-model="dialogs.configurations" :data="configurations"></config-view>
  </div>
</template>

<script>
module.exports = {
  components: {
    "add-admin": httpVueLoader("./AddAdmin.vue"),
    "add-escaltion-email": httpVueLoader("./AddEscalationEmail.vue"),
    "remove-admin": httpVueLoader("./RemoveAdmin.vue"),
    "identity-info": httpVueLoader("./IdentityInfo.vue"),
    "add-identity": httpVueLoader("./AddIdentity.vue"),
    "config-view": httpVueLoader("./ConfigurationsInfo.vue"),
  },
  data() {
    return {
      loading: {
        admins: false,
        identities: false,
        developerOptions: false,
        escalationEmails: false,
      },
      selectedAdmin: null,
      dialogs: {
        addAdmin: false,
        removeAdmin: false,
        identityInfo: false,
        addIdentity: false,
        escalationEmail: false,
        configurations: false,
      },
      admins: [],
      escalationEmails: [],
      identity: null,
      selectedIdentity: null,
      identities: [],
      configurations: null,
      testCert: false,
      overProvision: false,
      explorerLogs: false,
      escalationEmailsEnabled: false,
      sortNodesBySru: false,
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
    listEscaltionEmails() {
      this.loading.escalationEmails = true;
      this.$api.escalationEmails
        .list()
        .then((response) => {
          this.escalationEmails = JSON.parse(response.data).data;
        })
        .finally(() => {
          this.loading.escalationEmails = false;
        });
    },
    removeEscalationEmail(email) {
      console.log("this email should be removed", email);
      this.loading.escalationEmails = true;
      this.$api.escalationEmails
        .delete(email)
        .then((response) => {
          this.escalationEmails = JSON.parse(response.data).data;
        })
        .finally(() => {
          this.loading.escalationEmails = false;
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
      this.$api.identities
        .currentIdentity()
        .then((response) => {
          this.identity = JSON.parse(response.data).data;
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
    showConfig() {
      this.loading.developerOptions = true;
      this.$api.admins
        .getConfig()
        .then((response) => {
          this.configurations = JSON.parse(response.data).data;
        })
        .finally(() => {
          this.dialogs.configurations = true;
          this.loading.developerOptions = false;
        });
    },
    getDeveloperOptions() {
      this.loading.developerOptions = true;
      this.$api.admins
        .getDeveloperOptions()
        .then((response) => {
          let developerOptions = JSON.parse(response.data).data;
          this.testCert = developerOptions["test_cert"];
          this.overProvision = developerOptions["over_provision"];
          this.explorerLogs = developerOptions["explorer_logs"];
          this.escalationEmailsEnabled = developerOptions["escalation_emails"];
          this.sortNodesBySru = developerOptions["sort_nodes_by_sru"];
        })
        .finally(() => {
          this.loading.developerOptions = false;
        });
    },
    setDeveloperOptions() {
      this.$api.admins
        .setDeveloperOptions(
          this.testCert,
          this.overProvision,
          this.explorerLogs,
          this.escalationEmailsEnabled,
          this.sortNodesBySru
        )
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
    this.listEscaltionEmails();
  },
};
</script>
