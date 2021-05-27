<template>
  <div>
    <base-dialog
      :title="title"
      v-model="dialog"
      :error="error"
      :loading="loading"
    >
      <template
        v-if="action.name === 'generate' || action.name === 'edit'"
        #default
      >
        <p><span v-html="message"></span></p>
        <v-form ref="form">
          <v-text-field
            v-if="action.name === 'generate'"
            v-model="form.name"
            label="Key name"
            :rules="nameRules"
            required
          ></v-text-field>
          <v-select
            v-model="form.role"
            label="Select Role"
            :items="roles"
            :rules="[(v) => !!v || 'Role is required']"
            required
          ></v-select>
        </v-form>
      </template>
      <template v-else #default>
        <p><span v-html="message"></span></p>
      </template>
      <template #actions>
        <v-btn text @click="close">Close</v-btn>
        <v-btn text @click="execute(action.name)">{{
          action.buttonName
        }}</v-btn>
      </template>
    </base-dialog>
    <show-key v-model="dialogs.showKey" :apikey="key"></show-key>
  </div>
</template>

<script>
module.exports = {
  mixins: [dialog],
  props: {
    name: { type: String, default: "" },
    title: String,
    message: String,
    action: Object,
  },
  components: {
    "show-key": httpVueLoader("./ShowKey.vue"),
  },
  data() {
    return {
      key: null,
      oldName: null,
      dialogs: {
        showKey: false,
      },
      roles: USER_ROLES,
      regex: /^[a-z]([a-z0-9]*)$/,
      nameRules: [
        (v) => !!v || "Name is required",
        (v) =>
          (v && this.regex.test(v)) ||
          "Invalid value. It should be a valid identifier, all lowercase and starting with a letter, no spaces and no special characters",
      ],
    };
  },
  methods: {
    execute(name) {
      this[name]();
    },
    generate() {
      this.error = null;
      if (this.$refs.form.validate()) {
        this.loading = true;
        this.$api.apikeys
          .generate(this.form.name, this.form.role)
          .then((response) => {
            this.key = response.data.data.key;
            this.dialogs.showKey = true;
            this.done("Key is generated");
          })
          .catch((error) => {
            this.error = error.response.data;
          })
          .finally(() => {
            this.loading = false;
          });
      }
    },
    regenerate() {
      this.loading = true;
      this.$api.apikeys
        .regenerate(this.name)
        .then((response) => {
          this.key = response.data.data.key;
          this.dialogs.showKey = true;
          this.close();
        })
        .catch((error) => {
          this.error = error.response.data;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    edit() {
      this.error = null;
      if (this.$refs.form.validate()) {
        this.loading = true;
        this.$api.apikeys
          .edit(this.name, this.form.role)
          .then((response) => {
            this.done("Key is edited");
          })
          .catch((error) => {
            this.error = error.response.data;
          })
          .finally(() => {
            this.loading = false;
          });
      }
    },
    delete() {
      this.loading = true;
      this.error = null;
      this.$api.apikeys
        .delete(this.name)
        .then((response) => {
          this.done("Key is removed");
        })
        .catch((error) => {
          this.error = error.response.data;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    deleteAll() {
      this.loading = true;
      this.error = null;
      this.$api.apikeys
        .deleteAll()
        .then((response) => {
          this.done("All Keys are removed");
        })
        .catch((error) => {
          this.error = error.response.data;
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
  updated() {
    if (
      (this.oldName != this.name && this.action.name == "edit") ||
      (this.action.name == "generate" && this.dialog == true)
    ) {
      this.oldName = this.name;
      this.$refs.form.resetValidation();
    }
  },
};
</script>
