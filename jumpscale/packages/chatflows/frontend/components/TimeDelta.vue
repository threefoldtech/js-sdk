<template>
    <div>
      <Message :payload="payload"></Message>
      <v-text-field class="time-delta" v-model="val" height="50" placeholder="Time delta format" :rules="rules" readonly validate-on-blur outlined></v-text-field>
      <v-slider label="Years" v-model="years" thumb-label dense></v-slider>
      <v-slider label="Months" v-model="months" max="11" thumb-label dense></v-slider>
      <v-slider label="Weeks" v-model="weeks" max="3" thumb-label dense></v-slider>
      <v-slider label="Days" v-model="days" max="29" thumb-label dense></v-slider>
      <v-slider label="Hours" v-model="hours" max="23" thumb-label dense></v-slider>
    </div>
</template>

<script>
  module.exports = {
    mixins: [field],
    props: {payload: Object},
    data () {
      return {
        years: null,
        months: null,
        weeks: null,
        days: null,
        hours: null,
        validators: {
          is_valid: true
        }
      }
    },
    computed: {
      format () {
        return `${this.years}Y ${this.months}M ${this.weeks}w ${this.days}d ${this.hours}h`
      }
    },
    watch: {
      format (val) {
        this.val = val
      }
    },
    methods: {
      fromString () {
        let parts = this.val.split(" ")
        parts.forEach((part) => {
          if (part.length < 2) return 
          let name = part.slice(-1)
          let value = part.slice(0, -1)
          switch (name) {
            case "Y":
              this.years = value
              break
            case "M":
              this.months = value
              break
            case "w":
              this.weeks = value
              break
            case "d":
              this.days = value
              break
            case "h":
              this.hours = value
              break
          }
        })
      }
    },
    mounted () {
      this.$nextTick(() => {
        if (this.val) this.fromString()
      })
    }
  }
</script>

<style>
.time-delta input {
  font-size: 32px;
  text-align: center;
}
.time-delta .v-messages__message {
  text-align: center;
}
</style>