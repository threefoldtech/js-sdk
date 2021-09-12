<template>
  <div>
    <base-dialog title="Identity details" v-model="dialog" :loading="loading">
      <template #default>
        <v-simple-table v-if="identity">
          <template v-slot:default>
            <tbody>
              <tr>
                <td>Instance Name</td>
                <td>{{ name }}</td>
              </tr>
              <tr>
                <td>3Bot ID</td>
                <td>{{ identity.tid }}</td>
              </tr>
              <tr>
                <td>3Bot Name</td>
                <td>{{ identity.name }}</td>
              </tr>
              <tr>
                <td>Email</td>
                <td>{{ identity.email }}</td>
              </tr>
              <tr>
                <td>Explorer URL</td>
                <td>{{ identity.explorer_url }}</td>
              </tr>
              <tr>
                <td>Words</td>
                <td>
                  <v-text-field
                    hide-details
                    :value="identity.words"
                    readonly
                    solo
                    flat
                    :append-icon="showWords ? 'mdi-eye' : 'mdi-eye-off'"
                    :type="showWords ? 'text' : 'password'"
                    @click:append="showWords = !showWords"
                  ></v-text-field>
                </td>
              </tr>
              <tr>
                <td>admins</td>
                <td>
                  <v-chip
                    class="ma-2"
                    color="primary"
                    outlined
                    v-for="admin in identity.admins"
                    :key="admin"
                  >
                    {{ admin }}
                  </v-chip>
                </td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </template>
      <template #actions>
        <v-btn icon @click.stop="deleteIdentity">
          <v-icon color="primary" left>mdi-delete</v-icon>
        </v-btn>
        <v-btn text color="primary" :disabled="name == currentIdentity" @click.stop="shouldOpenConfirmation">Set Default</v-btn>
        <v-btn text class="text--lighten-1" color="red" @click.done="close">Close</v-btn>
      </template>
    </base-dialog>

    <admin-confirmation
      v-model="openConfirmation"
      @admin-confirm="setDefault"
      />
    </div>
</template>

<script>
module.exports = {
  components: {
    "admin-confirmation": httpVueLoader("./AdminConfirmation.vue"),
  },
  props: { name: String },
  mixins: [dialog],
  data() {
    return {
      identity: null,
      showWords: false,
      currentIdentity: null,
      openConfirmation: false
    };
  },
  watch: {
    dialog(val) {
      if (val) {
        this.getIdentityInfo();
        this.getCurrentIdentity();
      } else {
        this.identity = null;
      }
    },
  },
  methods: {
    getIdentityInfo() {
      this.loading = true;
      this.$api.identities
        .getIdentity(this.name)
        .then((response) => {
          this.identity = JSON.parse(response.data).data;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    getCurrentIdentity() {
      this.$api.identities
        .currentIdentity()
        .then((response) => {
          this.currentIdentity = JSON.parse(response.data).data;
        })
        .finally(() => {
          this.loading.identities = false;
        });
    },
    shouldOpenConfirmation() {
      if (this.identity.admins.length === 0) {
        return this.openConfirmation = true
      }
      this.setDefault();
    },
    setDefault() {
      this.openConfirmation = false;
      this.$api.identities
        .setIdentity(this.name)
        .then((response) => {
          this.$parent.$parent.$parent.$parent.getIdentity();
          this.done("Identity Updated", "success");
          window.location.reload();
        })
        .catch((error) => {
          console.log(error);
          this.alert("Failed to update identity", "error");
        })
        .finally(() => {
          this.dialog = false;
        });
    },
    deleteIdentity() {
      this.$api.identities
        .deleteIdentity(this.name)
        .then((response) => {
          responseMessage = JSON.parse(response.data).data;
          if (responseMessage == "Cannot delete current default identity") {
            this.alert(responseMessage, "error");
          } else {
            this.done("Identity deleted", "success");
          }
        })
        .catch((error) => {
          this.alert("Failed to delete identity", "error");
        })
        .finally(() => {
          this.dialog = false;
        });
    },
  },
};
</script>
