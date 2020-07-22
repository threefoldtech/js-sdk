<template>
  <div>
    <base-component title="Backup" icon="mdi-database" :loading="loading">
      
      <template #actions>
        <v-btn text @click.stop="dialogs.take = true">
          <v-icon left>mdi-plus</v-icon> Backup
        </v-btn>
        <v-switch v-model="autoBackup" single-line hide-details label="AUTO BACKUP"></v-switch>
      </template>

      <template #default>
      </template>

    </base-component>

    <take-backup v-model="dialogs.take"></take-backup>
  </div>
</template>

<script>
module.exports = {
  components: {
    'take-backup': httpVueLoader("./TakeBackup.vue")
  },
  data() {
    return {
      loading: false,
      snapshots: [],
      autoBackup: false,
      dialogs: {
        take: false
      }
    };
  },
  watch: {
    autoBackup () {
      this.changeAutoBackup()
    }
  },
  methods: {
    listSnapshots() {},
    changeAutoBackup () {
      console.log(this.autoBackup)
    }
  },
  mounted() {
    this.listSnapshots();
  }
};
</script>
