<template>
  <div>
    <base-component title="Backup" icon="mdi-database" :loading="loading">
      <template #actions>
        <v-btn text @click.stop="dialogs.take = true" :disabled="!inited">
          <v-icon left>mdi-plus</v-icon>Backup
        </v-btn>
        <v-switch
          v-model="autoBackup"
          :disabled="!inited"
          single-line
          hide-details
          label="AUTO BACKUP"
        ></v-switch>
      </template>

      <template #default>
        <v-alert v-if="!inited" text prominent class="ma-5" border="right" type="info">
          <span>Your repo is not inited, plesaed init it first</span>
          <v-btn
            text
            class="ml-5"
            color="info"
            :loading="loadings.init"
            @click.stop="dialogs.init = true"
          >Init now</v-btn>
        </v-alert>
      </template>
    </base-component>
    <init-repos v-model="dialogs.init"></init-repos>
    <take-backup v-model="dialogs.take"></take-backup>
  </div>
</template>

<script>
module.exports = {
  components: {
    "take-backup": httpVueLoader("./TakeBackup.vue"),
    "init-repos": httpVueLoader("./InitRepos.vue")
  },
  data() {
    return {
      loading: false,
      snapshots: [],
      autoBackup: false,
      inited: true,
      loadings: {
        init: false
      },
      dialogs: {
        take: false,
        init: false
      }
    };
  },
  watch: {
    autoBackup() {
      this.changeAutoBackup();
    }
  },
  methods: {
    checkReposInit() {
      this.$api.miniobackup
        .inited()
        .then(response => {
          this.inited = response.data;
        })
        .catch(error => {
          this.error = error.message;
        });
    },
    checkAutoBackup() {
      this.$api.miniobackup
        .enabled()
        .then(response => {
          this.autoBackup = response.data;
        })
        .catch(error => {
          this.error = error.message;
        });
    },
    changeAutoBackup() {
      if (this.autoBackup == true) {
        this.$api.miniobackup
          .enable()
          .then(response => {
            this.done("Auto backup is enabled");
          })
          .catch(error => {
            this.error = error.message;
          })
          .finally(() => {
            this.loading = false;
          });
      } else {
        this.$api.miniobackup
          .disable()
          .then(response => {
            this.done("Auto backup is disbaled");
          })
          .catch(error => {
            this.error = error.message;
          })
          .finally(() => {
            this.loading = false;
          });
      }
    }
  },
  mounted() {
    this.checkReposInit();
    this.checkAutoBackup();
  }
};
</script>
