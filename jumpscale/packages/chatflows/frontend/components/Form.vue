<template>
  <div>
    <Message :payload="payload"></Message>
    <component 
      v-for="(field, i) in payload.fields" 
      :key="i" 
      :ref="`field-${i}`"
      :payload="field" 
      v-bind:is="categories[field.category]" 
      v-model="val[i]"
    />
  </div>
</template>

<script>  
  module.exports = {
    mixins: [field],
    props: {payload: Object}
  }
</script>
