<template>
<div>
  <base-component title="Packages" icon="mdi-package-variant-closed" :loading="loading">

    <template #actions>
      <v-btn color="primary" text @click.stop="addDialog = true">
        <v-icon left>mdi-plus</v-icon> Add
      </v-btn>
    </template>

    <template #default>
      <v-row align="start" justify="start">
        <v-card class="ma-4 mt-2" width="300" v-for="pkg in packages" :key="pkg.name">
          <v-card-title class="primary--text">{{pkg.name}}</v-card-title>

          <v-card-subtitle v-if="pkg.system_package">
            System Package
          </v-card-subtitle>

          <v-card-text>{{pkg.path}}</v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn v-if="!pkg.system_package" icon @click.stop="selected = pkg.name; deleteDialog = true">
              <v-icon color="primary" left>mdi-delete</v-icon>  
            </v-btn>
          </v-card-actions>
        </v-card>
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
    methods: {
      listPackages () {
        this.loading = true
        this.$api.packages.list().then((response) => {
          this.packages = JSON.parse(response.data).data
        }).finally (() => {
          this.loading = false
        })
      }
    },
    mounted () {
      this.listPackages()
    }
  }
</script>
