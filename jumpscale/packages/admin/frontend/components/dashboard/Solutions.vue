<template>
  <base-section title="Solutions" icon="mdi-apps" :loading="loading">
    <v-chip
      class="mr-2 mb-2"
      outlined
      v-for="(solution, i) in solutions"
      :key="i"
      :to="solution.url"
    >{{solution.name}}</v-chip>
  </base-section>
</template>

<script>
module.exports = {
  data() {
    return {
      loading: false,
      solutions: [...Object.values(SOLUTIONS)],
    };
  },
};
</script>
