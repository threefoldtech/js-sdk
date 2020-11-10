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
        <v-tab readonly>Time</v-tab>
      </v-tabs>

      <v-tabs-items v-model="tab">
        <v-tab-item>
          <v-date-picker
            v-if="tab === 0"
            v-model="date"
            color="primary"
            :min="new Date(this.minTime * 1000).toISOString()"
            @click:date="tab = date ? 1 : 0"
            no-title
            scrollable
          />
        </v-tab-item>
        <v-tab-item>
          <v-time-picker
            v-if="tab === 1"
            v-model="time"
            color="primary"
            @change="save"
            no-title
            scrollable
          />
        </v-tab-item>
      </v-tabs-items>
    </v-menu>
  </div>
</template>

<script>
module.exports = {
  mixins: [field],
  props: {
    payload: Object,
  },
  data() {
    return {
      tab: 0,
      menu: false,
      date: null,
      time: null,
      minTime: this.payload.kwargs.min_time ? Date.now()/1000 + this.payload.kwargs.min_time[0]:null ,
      dateTime: null,
      validators: {
        is_valid: true,
      },
    };
  },
  watch: {
    date() {
      this.update();
    },
    time() {
      this.update();
    },
  },
  methods: {
    setValue() {
      let datetime =
        this.date && this.time
          ? new Date(`${this.date} ${this.time}`)
          : new Date();
      this.dateTime = datetime.toLocaleString('en-GB');
      this.val = Math.floor(datetime.getTime() / 1000);
    },
    setDateTimeValue() {
      let value = this.val; // value here in seconds
      this.dateTime = new Date(value * 1000).toLocaleString("en-GB");
    },
    update() {
      if (this.date && this.time) this.setValue();
    },
    save() {
      this.tab = 0;
      this.menu = false;
    },
  },
  mounted() {
    this.time = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
    this.$nextTick(() => {
      if (this.val) {
        this.setDateTimeValue();
      } else {
        this.setValue();
      }
    });
  },
};
</script>
