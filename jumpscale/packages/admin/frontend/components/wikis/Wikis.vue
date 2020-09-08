<template>
  <base-component title="Threefold Wikis" icon="mdi-book-open-outline" :loading="loading">
    <template #default>
      <v-row align="start" justify="start">
        <v-card class="ma-4 mt-2" width="300" v-for="wiki in wikis" :key="wiki.title" :to="wiki.path">
          <v-card-title>{{wiki.title}}</v-card-title>
          <v-card-text>
            <a :href="wiki.url">{{wiki.url}}</a>
          </v-card-text>
        </v-card>
      </v-row>
    </template>
  </base-component>
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
