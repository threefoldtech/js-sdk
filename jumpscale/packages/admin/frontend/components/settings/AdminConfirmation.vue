<template>
  <base-dialog title="Admin Confirmation" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      No admins were found. Are you sure you want to set as default ?
    </template>
    <template #actions>
      <v-btn text @click="close">No</v-btn>
      <v-btn text @click="$emit('admin-confirm')" color="red">Yes</v-btn>
    </template>
  </base-dialog>  
</template>

<script>

module.exports = {
  mixins: [dialog]
}
</script>
