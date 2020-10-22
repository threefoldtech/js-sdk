<template>
  <base-dialog title="Chatflows" v-model="dialog" :loading="loading">
    <template #default>
      <v-chip
        class="mr-2 mb-2"
        outlined
        v-for="(endpoint,i) in chatflowEndpoints"
        :key="i"
        :href="endpoint.url"
      >{{ endpoint.name }}</v-chip>

    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  props: { name: String},
  mixins: [dialog],
  data() {
    return {
      chatflowEndpoints: null,
    };
  },
  watch: {
    dialog(val) {
      if (val) {
        this.getChatflows();
      } else {
        this.chatflowEndpoints = null;
      }
    },
  },
  methods: {
    getChatflows() {
      this.loading = true;
      this.$api.packages
        .listChatEndpoints(this.name)
        .then((response) => {
          this.chatflowEndpoints = JSON.parse(response.data).data;
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
};
</script>
