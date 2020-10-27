<template>
  <base-dialog v-if="data" :title="data.id" v-model="dialog">
    <template #default>
        <v-sheet v-if="data.sshkey" class="pa-5">
            <p>{{data.sshkey}}</p>
        </v-sheet>
    </template>
    <template #actions>
      <v-btn text color="error" @click="close">Close</v-btn>
    </template>
  </base-dialog>
</template>
<script>

module.exports = {
  props: ["data"],
  mixins: [dialog],
}
</script>

<style scoped>
  p {
    white-space: normal;
    word-wrap: break-word;
  }
</style>
