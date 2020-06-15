<template>
  <div>
    <Message :payload="payload"></Message>
    <v-row class="my-0 py-0" v-for="(item, key, index) in val" :key="index">
      <v-col class="my-0 py-0" cols="12" md="4">
        <v-text-field :value="key" solo flat dense readonly></v-text-field>
      </v-col>
      <v-col class="my-0 py-0" cols="12" md="4">
        <v-text-field :value="item" solo flat dense readonly></v-text-field>
      </v-col>
      <v-col class="my-0 py-0" cols="12" md="4">
        <v-btn icon @click="remove(key)" color="primary">
          <v-icon>mdi-delete</v-icon>
        </v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="4">
        <v-text-field v-model="k" label="Name" dense outlined></v-text-field>
      </v-col>
      <v-col cols="12" md="4">
        <v-text-field v-model="v" label="Value" dense outlined></v-text-field>
      </v-col>
      <v-col cols="12" md="4">
        <v-btn icon @click="add" color="primary">
          <v-icon>mdi-plus</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script>
  module.exports = {
    mixins: [field],
    props: {payload: Object},
    data () {
      return {
        k: null,
        v: null
      }
    },
    methods: {
      add () {
        this.$set(this.val, this.k, this.v)
        this.reset()
      },
      reset () {
        this.k = null
        this.v = null
      },
      remove (k) {
        this.$delete(this.val, k)
      }
    },
    mounted () {
      this.$nextTick(() => {
        if (!this.val) {
          this.val = {}
        }
      })
    }
  }
</script>
