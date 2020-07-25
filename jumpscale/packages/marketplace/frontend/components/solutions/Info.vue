<template>
  <base-dialog title="Solution info" v-model="dialog" :loading="loading">
    <template #default>
      <code-area mode="python" :content="json"></code-area>
    </template>
    <template #actions>
      <v-btn text @click.stop="close">Close</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  props: { data: Object },
  mixins: [dialog],
  computed: {
    json() {
      return JSON.stringify(JSON.parse(this.data.reservation), null, 2);
    }
  }
};
</script>
