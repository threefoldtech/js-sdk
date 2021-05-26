<template>
  <v-snackbar v-model="show" :color="status" :timeout="5000" right top>
    {{ msg }}
  </v-snackbar>
</template>

<script>
module.exports = {
  props: ["msg"],
  data() {
    return {
      show: false,
      status: "success",
    };
  },
  mounted() {
    if (this.msg) {
      this.show = true;
    }
  },
};
</script>
