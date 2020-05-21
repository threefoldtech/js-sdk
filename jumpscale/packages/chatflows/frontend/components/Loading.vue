<template>
  <div class="text-center">
    <Message :payload="payload"></Message>
    <v-progress-circular
      :rotate="-90"
      :size="150"
      :width="15"
      :value="payload.value"
      color="primary"
    >
      <strong>{{ payload.value }} %</strong>
    </v-progress-circular>
  </div>
</template>

<script>  
  module.exports = {
    mixins: [field],
    props: {payload: Object}
  }
</script>