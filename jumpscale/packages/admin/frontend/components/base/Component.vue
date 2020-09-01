<template>
  <div style="padding: 40px; padding-top:20px">
    <v-toolbar color="transparent" flat>
      <v-toolbar-title class="primary--text">
        <v-icon color="primary" large left>{{icon}}</v-icon>
        {{title}}
      </v-toolbar-title>

      <v-spacer></v-spacer>
      <slot name="search"></slot>

      <v-spacer></v-spacer>
      <slot name="actions"></slot>
    </v-toolbar>

    <v-divider></v-divider>
    <br />
    <div v-if="loading" class="loading text-center">
      <v-progress-circular :size="100" :width="7" color="primary" indeterminate></v-progress-circular>
    </div>
    <slot v-else name="default"></slot>
  </div>
</template>

<script>
module.exports = {
  props: {
    title: String,
    icon: String,
    loading: Boolean,
  },
};
</script>

<style scoped>
div.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}
</style>
