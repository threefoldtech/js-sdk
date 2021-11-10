<template>
  <div v-html="html"></div>
</template>

<script>
module.exports = {
  props: { payload: Object },
  computed: {
    html() {
      return marked.parse(this.payload.msg);
    },
  },
};
</script>

<style scoped>
code {
  padding: 7px;
  margin: 10px 0px;
}

h1,
h2,
h3 {
  font-weight: 600 !important;
  font-family: sans-serif !important;
}

span,
p,
ul,
li,
code {
  font-size: 18px;
  line-height: 140%;
}

li {
  margin-bottom: 8px;
}
</style>
