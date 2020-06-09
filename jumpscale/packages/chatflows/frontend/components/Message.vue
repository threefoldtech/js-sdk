<template>
  <div class="mb-4">
    <Markdown v-if="payload.kwargs.md" :payload="payload"></Markdown>
    <div v-else-if="payload.kwargs.html" v-html="payload.msg"></div>
    <h3 v-else class="title font-regular">{{payload.msg}}</h3>
  </div>
</template>

<script>
  module.exports = {
    props: {payload: Object}
  }
</script>
