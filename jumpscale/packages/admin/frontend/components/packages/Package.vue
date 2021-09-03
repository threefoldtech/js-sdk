<template>
  <div>
  <v-card class="ma-4 mt-2" width="300" :loading="loading" :disabled="loading">
    <v-card-title class="primary--text">{{pkg.ui_name}}</v-card-title>
    <v-card-subtitle v-if="pkg.system_package">System Package</v-card-subtitle>
    <v-card-text style="height:75px">
      {{pkg.path.length > PACKAGE_PATH_MAXLENGTH ?
      pkg.path.slice(0, PACKAGE_PATH_MAXLENGTH) + "..." :
      pkg.path}}
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon v-if="pkg.installed && !pkg.system_package" @click="$emit('delete', pkg.name)">
            <v-icon v-bind="attrs" v-on="on" color="primary">mdi-trash-can-outline</v-icon>
          </v-btn>
        </template>
        <span>Delete</span>
      </v-tooltip>

      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon v-if="pkg.installed && pkg.frontend" :href="pkg.frontend">
            <v-icon v-bind="attrs" v-on="on" color="primary">mdi-web</v-icon>
          </v-btn>
        </template>
        <span>Open in browser</span>
      </v-tooltip>

      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon v-if="pkg.installed && pkg.chatflows" @click="showChatflows()">
            <v-icon v-bind="attrs" v-on="on" color="primary">mdi-chat</v-icon>
          </v-btn>
        </template>
        <span>Chatflows</span>
      </v-tooltip>

      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon v-if="pkg.installed" @click="reload(pkg.name)">
            <v-icon v-bind="attrs" v-on="on" color="primary">mdi-reload</v-icon>
          </v-btn>
        </template>
        <span>Reload</span>
      </v-tooltip>

      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon v-if="!pkg.installed" :href="pkg.frontend" :loading="loading" @click="install">
            <v-icon v-bind="attrs" v-on="on" color="primary">mdi-archive-arrow-down-outline</v-icon>
          </v-btn>
        </template>
        <span>Install</span>
      </v-tooltip>
    </v-card-actions>
  </v-card>
  <open-chatflows v-model="dialogs.openChatflows" :name="pkg.name"></open-chatflows>
  </div>
</template>

<script>
module.exports = {
  components: {
    'open-chatflows': httpVueLoader("./Chats.vue"),
  },
  props: {
    pkg: Object,
  },
  data() {
    return {
      loading: false,
      PACKAGE_PATH_MAXLENGTH: 80,
      dialogs: {
        openChatflows: false,
      },
    };
  },
  methods: {
    install() {
      this.loading = true;
      this.$api.packages
        .add(this.pkg.path)
        .then((response) => {
          this.alert("Package is added", "success");
          this.$emit("update", this.pkg.name);
        })
        .catch((error) => {
          this.alert(error.response.data.message, "error");
        })
        .finally(() => {
          this.loading = false;
        });
    },
    reload() {
      this.loading = true;
      this.$api.packages
        .add(this.pkg.path)
        .then((response) => {
          this.alert("Package is reloaded", "success");
          this.$emit("update", this.pkg.name);
        })
        .catch((error) => {
          this.alert(error.response.data.message, "error");
        })
        .finally(() => {
          this.loading = false;
        });
    },
    showChatflows() {
      this.dialogs.openChatflows = true;
    },
  },
};
</script>
