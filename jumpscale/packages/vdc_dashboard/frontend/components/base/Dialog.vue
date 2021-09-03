<template>
  <v-dialog v-model="dialog" width="700">
    <v-card :loading="loading" :disabled="loading">
      <v-card-title class="headline">{{ title }}</v-card-title>
      <v-card-text :class="`pa-5 ${textcolor}--text`" :color="textcolor">
        <v-alert v-if="error" dense outlined type="error" class="mb-5">
          {{ error }}
        </v-alert>

        <slot name="default"></slot>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <slot name="actions"></slot>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
module.exports = {
  props: {
    value: Boolean,
    title: String,
    error: String,
    loading: Boolean,
    textcolor: { type: String, default: "black" },
  },
  computed: {
    dialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
};
</script>
