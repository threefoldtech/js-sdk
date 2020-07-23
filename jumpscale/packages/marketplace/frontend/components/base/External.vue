<template>
  <div>
    <v-row v-if="iframeLoading" style="height:100%" align="center" justify="center">
      <v-progress-circular size="100" width="5" color="primary" indeterminate></v-progress-circular>
    </v-row>
    <iframe :src="url" style="border:none" height="100%" width="100%" @load="iframeLoading = false"></iframe>
  </div>
</template>

<script>
module.exports = {
  props: {
    url: String,
  },
  data() {
    return {
      iframeLoading: true,
    }
  },
  methods: {
  },
  mounted() {
  }
};
</script>
