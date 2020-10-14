<template>
  <div>
    <base-section title="Marketplace" icon="mdi-shopping-outline" :loading="loading">
      <template #actions>
        <v-btn text @click.stop="dialogs.take = true" :disabled="!inited">
          <v-icon left>mdi-backup-restore</v-icon>Backup
        </v-btn>
        <v-switch
          v-model="autoBackup"
          :disabled="!inited"
          single-line
          hide-details
          label="Auto backup"
          dense
        ></v-switch>
      </template>

      <template #default>
        <v-alert v-if="!inited" text prominent class="ma-5" border="right" type="info">
          <span>Your repo is not inited, please init it first</span>
          <v-btn
            text
            class="ml-5"
            color="info"
            :loading="loadings.init"
            @click.stop="dialogs.init = true"
          >Init now</v-btn>
        </v-alert>

        <v-list v-if="inited" three-line>
          <v-subheader>Snapshots</v-subheader>
          <v-list-item v-for="snapshot in snapshots" :key="snapshot.id">
            <v-list-item-avatar>
              <v-icon>mdi-layers-outline</v-icon>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title v-html="snapshot.id"></v-list-item-title>
              <v-list-item-subtitle>{{new Date(snapshot.time).toLocaleString('en-GB')}}</v-list-item-subtitle>
              <v-list-item-subtitle>
                <v-chip
                  v-for="tag in snapshot.tags"
                  :key="snapshot.id + tag"
                  class="mr-1 mt-2"
                  small
                  outlined
                >{{ tag }}</v-chip>
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </template>
    </base-section>
    <init-repos v-model="dialogs.init"></init-repos>
    <take-backup v-model="dialogs.take" @done="listSnapshots"></take-backup>
  </div>
</template>

<script>
module.exports = {
  mixins: [dialog],
  components: {
    "take-backup": httpVueLoader("./TakeBackup.vue"),
    "init-repos": httpVueLoader("./InitRepos.vue"),
  },
  data() {
    return {
      loading: false,
      snapshots: [],
      autoBackup: false,
      inited: true,
      loadings: {
        init: false,
      },
      dialogs: {
        take: false,
        init: false,
      },
    };
  },
  watch: {
    autoBackup() {
      this.changeAutoBackup();
    },
  },
  methods: {
    enableAutoBackup() {
      this.$api.mrktbackup
        .enable()
        .then((response) => {
          this.autoBackup = true;
        })
        .catch((error) => {
          this.error = error.response.data.message;
        });
    },
    checkReposInit() {
      this.$api.mrktbackup
        .inited()
        .then((response) => {
          this.inited = response.data;
          if (this.inited) {
            this.checkAutoBackup();
            this.enableAutoBackup();
            this.listSnapshots();
          }
        })
        .catch((error) => {
          this.error = error.message;
        });
    },
    listSnapshots() {
      this.$api.mrktbackup
        .snapshots()
        .then((response) => {
          this.snapshots = JSON.parse(response.data).data;
        })
        .catch((error) => {
          this.error = error.response.data.message;
        });
    },
    checkAutoBackup() {
      this.$api.mrktbackup
        .enabled()
        .then((response) => {
          this.autoBackup = response.data;
        })
        .catch((error) => {
          this.error = error.response.data.message;
        });
    },
    changeAutoBackup() {
      if (this.autoBackup == true) {
        this.$api.mrktbackup
          .enable()
          .then((response) => {
            this.done("Auto backup is enabled");
          })
          .catch((error) => {
            this.error = error.response.data.message;
          })
          .finally(() => {
            this.loading = false;
          });
      } else {
        this.$api.mrktbackup
          .disable()
          .then((response) => {
            this.done("Auto backup is disabled");
          })
          .catch((error) => {
            this.error = error.response.data.message;
          })
          .finally(() => {
            this.loading = false;
          });
      }
    },
  },
  mounted() {
    this.checkReposInit();
  },
};
</script>
