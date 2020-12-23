<template>
<div>
  <base-component title="Packages" icon="mdi-package-variant-closed" :loading="loading">

    <template #actions>
      <v-btn color="primary" text @click.stop="addDialog = true">
        <v-icon left>mdi-plus</v-icon> Add
      </v-btn>
    </template>

    <template #default>

      <span v-if="allPackages.system.length" class="subtitle-1">System Packages</span>
      <v-row class="mt-2" align="start" justify="start">
        <package-info v-for="pkg in allPackages.system" :key="pkg.name" :pkg="pkg" @update="listPackages" @delete="deletePackage"></package-info>
      </v-row><br>

      <span v-if="allPackages.installed.length" class="subtitle-1">Installed Packages</span>
      <v-row class="mt-2" align="start" justify="start">
        <package-info v-for="pkg in allPackages.installed" :key="pkg.name" :pkg="pkg" @update="listPackages" @delete="deletePackage"></package-info>
      </v-row><br>

      <span v-if="allPackages.available.length" class="subtitle-1">Available Packages</span>
      <v-row class="mt-2" align="start" justify="start">
        <package-info v-for="pkg in allPackages.available" :key="pkg.name" :pkg="pkg" @update="listPackages" @delete="deletePackage"></package-info>
      </v-row>

    </template>
  </base-component>

  <add-package v-model="addDialog" @done="listPackages"></add-package>
  <delete-package v-model="deleteDialog" :name="selected" @done="listPackages"></delete-package>

  </div>
</template>

<script>

  module.exports = {
    components: {
      'package-info': httpVueLoader("./Package.vue"),
      'add-package': httpVueLoader("./Add.vue"),
      'delete-package': httpVueLoader("./Delete.vue"),
    },
    data () {
      return {
        loading: false,
        packages: [],
        selected: null,
        addDialog: false,
        deleteDialog: false
      }
    },
    computed: {
      allPackages () {
        let packages = {system: [], installed: [], available: []}
        this.packages.forEach((package) => {
          if (package.system_package) packages.system.push(package)
          else if (package.installed) packages.installed.push(package)
          else packages.available.push(package)
        })
        return packages
      }
    },
    methods: {
      listPackages () {
        this.loading = true
        this.$emit("updatesidebarlist");
        this.$api.packages.list().then((response) => {
          this.packages = JSON.parse(response.data).data
        }).finally (() => {
          this.loading = false
        })
      },
      deletePackage (pkg) {
        this.selected = pkg
        this.deleteDialog = true
      }
    },
    mounted () {
      this.listPackages()
    }
  }
</script>
