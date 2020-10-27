<template>
  <base-dialog title="SSH Key" v-model="dialog">
    <template #default>
        <v-sheet v-if="sshkey" class="pa-5">
            <p>{{sshkey}}</p>
        </v-sheet>
    </template>
    <template #actions>
      <v-btn text color="error" @click="close">Close</v-btn>
    </template>
  </base-dialog>
</template>
<script>

module.exports = {
  props: ["sshkey"],
  mixins: [dialog],
}
</script>

<style scoped>
  p {
    white-space: normal;
    word-wrap: break-word;
  }
</style>
