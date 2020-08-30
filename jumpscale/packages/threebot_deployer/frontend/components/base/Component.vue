<template>
  <div style="padding: 40px; padding-top:20px">
    <v-toolbar color="transparent" flat>
      <v-toolbar-title class="primary--text">
        <v-icon color="primary" large left>{{icon}}</v-icon> {{title}}
      </v-toolbar-title>

      <v-spacer></v-spacer>
      <slot name="search"></slot>

      <v-spacer></v-spacer>
      <slot name="actions"></slot>
    </v-toolbar>

    <v-divider></v-divider><br>
    <slot name="default"></slot>
  </div>
</template>

<script>
  module.exports = {
    props: {
      title: String,
      icon: String,
      loading: Boolean
    }
  }
</script>
