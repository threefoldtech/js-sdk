<template>
  <div>
    <base-component title="Backup" icon="mdi-database" :loading="loading">
      <template #default>
        <v-tabs class="justify-start" background-color="transparent" vertical>
          <v-tab>Marketplace</v-tab>
          <v-tab>Minio</v-tab>
          <v-tab-item class="ml-5">
            <marketplace></marketplace>
          </v-tab-item>
          <v-tab-item class="ml-5">
            <minio></minio>
          </v-tab-item>
        </v-tabs>
      </template>
    </base-component>
  </div>
</template>

<script>
module.exports = {
  components: {
    marketplace: httpVueLoader("./marketplace/Backup.vue"),
    minio: httpVueLoader("./minio/Backup.vue"),
  },
  data() {
    return {
      loading: false,
    };
  },
};
</script>

<style scoped>
.v-tab.v-tab {
  justify-content: flex-start;
}
</style>
