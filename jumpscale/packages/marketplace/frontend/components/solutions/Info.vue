<template>
  <base-dialog title="Solution info" v-model="dialog" :loading="loading">
    <template #default>
      <pre>
        {{JSON.stringify(JSON.parse(data.reservation.json),null,2)}}
      </pre>
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
}
</script>
