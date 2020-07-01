<template>
  <base-dialog title="Solution details" v-model="dialog" :loading="loading">
    <template #default>
      <code-area mode="python" :content="json"></code-area>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
    </template>
  </base-dialog>  
</template>

<script>

module.exports = {
  props: {data: Object},
  mixins: [dialog],
  computed: {
    json () {
      return JSON.stringify(JSON.parse(this.data.reservation.json), null, 2)
    }
  }
}
</script>

