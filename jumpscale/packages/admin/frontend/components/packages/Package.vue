<template>
  <v-card class="ma-4 mt-2" width="300" :loading="loading" :disabled="loading">
    <v-card-title class="primary--text">{{pkg.name}}</v-card-title>
    <v-card-subtitle v-if="pkg.system_package">System Package</v-card-subtitle>
    <v-card-text style="height:75px">
      {{pkg.path.length > PACKAGE_PATH_MAXLENGTH ?
      pkg.path.slice(0, PACKAGE_PATH_MAXLENGTH) + "..." :
      pkg.path}}
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn icon v-if="pkg.installed && !pkg.system_package" @click="$emit('delete', pkg.name)">
        <v-icon color="primary">mdi-trash-can-outline</v-icon>
      </v-btn>

      <v-btn icon v-if="pkg.installed && pkg.frontend" :href="pkg.frontend">
        <v-icon color="primary">mdi-web</v-icon>
      </v-btn>

      <v-btn icon v-if="!pkg.installed" :href="pkg.frontend" :loading="loading" @click="install">
        <v-icon color="primary">mdi-archive-arrow-down-outline</v-icon>
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
module.exports = {
  props: {
    pkg: Object,
  },
  data() {
    return {
      loading: false,
      PACKAGE_PATH_MAXLENGTH: 80,
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
  },
};
</script>
