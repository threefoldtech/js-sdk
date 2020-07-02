<template>
  <base-section title="Wikis" icon="mdi-book-open-outline" :loading="loading">
    <v-chip :to="wiki.path" class="mr-2 mb-2" outlined v-for="(wiki, i) in wikis" :key="i">
      {{wiki.title}}
    </v-chip>
  </base-section>
</template>

<script>
  module.exports = {
    data () {
      return {
        loading: false,
        wikis: Object.values(WIKIS)
      }
    }
  }
</script>
