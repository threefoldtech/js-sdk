<template>
  <div class="text-center">
    <Message :payload="payload"></Message>
    <v-progress-circular
      indeterminate
      :size="150"
      :width="15"
      color="primary"
    >
    </v-progress-circular>
  </div>
</template>

<script>  
  module.exports = {
    mixins: [field],
    props: {payload: Object}
  }
</script>