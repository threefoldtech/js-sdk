<template>
  <div>
    <Message :payload="payload"></Message>
    <v-menu v-model="menu" :close-on-content-click="false" min-width="290">
      <template v-slot:activator="{ on }">
        <v-text-field
          v-model="dateTime"
          v-on="on"
          readonly
          outlined
          @click="menu = true"
          :rules="rules"
          prepend-inner-icon="mdi-calendar-month"
          validate-on-blur
        />
      </template>

      <v-tabs v-model="tab">
        <v-tab>Date</v-tab>
        <v-tab readOnly>Time</v-tab>
      </v-tabs>

      <v-tabs-items v-model="tab">
        <v-tab-item>
          <v-date-picker v-if="tab === 0" v-model="date" color="primary" @click:date="tab = date ? 1 : 0;" no-title scrollable/>
        </v-tab-item>
        <v-tab-item>
          <v-time-picker v-if="tab === 1" v-model="time" color="primary" @change="save" no-title scrollable/> 
        </v-tab-item>
      </v-tabs-items>
    </v-menu>
  </div>

</template>

<script>
  module.exports = {
    mixins: [field],
    props: {payload: Object},
    data () {
      return {
        tab: 0,
        menu: false,
        date: null,
        time: null,
        dateTime: null,
        validators: {
          is_valid: true
        }
      }
    },
    watch: {
      date () {
        this.update()
      },
      time () {
        this.update()
      }
    },
    methods: {
      update () {
        if (this.date && this.time) {
          let datetime = new Date(`${this.date} ${this.time}`)
          this.dateTime = datetime.toLocaleString()
          this.val = datetime.getTime() / 1000
        }
      },
      save () {
        this.tab = 0
        this.menu = false
      }
    },
    mounted () {
      this.$nextTick(() => {
        if (this.val){
          this.dateTime = new Date(this.val * 1000).toLocaleString()
        } else {
          let datetime = new Date()
          this.dateTime = datetime.toLocaleString()
          this.val = Math.floor(datetime.getTime() / 1000)
        }
      })
    }
  }
</script>
