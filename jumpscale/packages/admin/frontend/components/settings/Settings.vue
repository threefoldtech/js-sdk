<template>
  <div>
    <base-component title="Setting" icon="mdi-tune">
      <template #actions>
      </template>

      <template #default>
        <v-row align="start" justify="start">

          <v-col class="mt-0 pt-0" cols="12" md="4">
            <base-section title="Explorer" icon="mdi-earth" :loading="loading.explorers">
            <v-radio-group v-model="explorer" :mandatory="false" @change="setExplorer">
              <v-radio v-for="(explorer, i) in explorers" :key="i" :label="explorer.name" :value="explorer.type"></v-radio>
            </v-radio-group>
            </base-section>
          </v-col>

          <v-col class="mt-0 pt-0" cols="12" md="4">

            <base-section title="Admins" icon="mdi-account-lock" :loading="loading.admins">
              <template #actions>
                <v-btn text @click.stop="dialogs.addAdmin = true">
                  <v-icon left>mdi-plus</v-icon> Add
                </v-btn>
              </template>

              <v-chip class="ma-2" color="primary" min-width="50" v-for="admin in admins" :key="admin" @click:close="removeAdmin(admin)" outlined label close close-icon="mdi-close-circle-outline">
                {{ admin }}
              </v-chip>
            </base-section>

          </v-col>
        </v-row>
      </template>
    </base-component>
    
    <add-admin v-model="dialogs.addAdmin" @done="listAdmins"></add-admin>
    <remove-admin v-model="dialogs.removeAdmin" :name="selectedAdmin" @done="listAdmins"></remove-admin>
  
  </div>
</template>

<script>
  module.exports = {
    components: {
      'add-admin': httpVueLoader("./AddAdmin.vue"),
      'remove-admin': httpVueLoader("./RemoveAdmin.vue"),
    },
    data () {
      return {
        loading: {
          explorers: false,
          admins: false,
        },
        selectedAdmin: null,
        dialogs: {
          addAdmin: false,
          removeAdmin: false
        },
        admins: [],
        explorers: [
          {name: "Main Network", url: "https://explorer.grid.tf", type: "main"},
          {name: "Test Network", url: "https://explorer.testnet.grid.tf", type: "testnet"}
        ],
        explorer: null
      }
    },
    methods: {
      listAdmins () {
        this.loading.admins = true
        this.$api.admins.list().then((response) => {
          this.admins = JSON.parse(response.data).data
        }).finally(() => {
          this.loading.admins = false
        })
      },
      removeAdmin (name) {
        this.selectedAdmin = name
        this.dialogs.removeAdmin = true
      },
      getCurrentExplorer () {
        this.loading.explorers = true
        this.$api.explorers.get().then((response) => {
          this.explorer = JSON.parse(response.data).data.type
        }).finally(() => {
          this.loading.explorers = false
        })
      },
      setExplorer (explorer) {
        this.$api.admins.setExplorer(explorer).then((response) => {
          this.alert("Explorer is updated", "success")
        }).catch((error) => {
          this.alert("Failed to update explorer", "error")
        })
      },      
    },
    mounted () {
      this.listAdmins()
      this.getCurrentExplorer()
    }
  }
</script>
