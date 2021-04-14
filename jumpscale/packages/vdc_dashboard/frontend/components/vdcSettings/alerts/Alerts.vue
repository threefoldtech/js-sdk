<template>
  <div>
    <base-component title="Alerts" icon="mdi-alert-outline" :loading="loading">
      <template #default>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field>
        <v-data-table class="elevation-1" :loading="loading" :search="search" :headers="headers" :items="alerts" @click:row="open"  :sort-by="['id']" :sort-desc="[true]" :page.sync="page">
          <template slot="no-data">No Alerts available</p></template>
          <template v-slot:item.message="{ item }">
            {{ item.message.slice(0, 50) }} {{ item.message.length > 50 ? '...' : ''}}
           </template>

           <template v-slot:item.last_occurrence="{ item }">
            {{ new Date(item.last_occurrence * 1000).toLocaleString('en-GB') }}
          </template>
        </v-data-table>
      </template>
    </base-component>

    <show-alert v-if="selected" v-model="dialogs.show" :alertdata="selected"></show-alert>
  </div>
</template>


<script>
module.exports = {
  props: {
    alertid: {
      type: Number,
      default: null,
    },
  },
  components: {
    "show-alert": httpVueLoader("./Alert.vue"),
  },
  data() {
    return {
      search: "",
      alerts: [],
      selected: null,
      page: 1,
      dialogs: {
        show: false,
      },
      loading: false,
      headers: [
        { text: "Id", value: "id" },
        { text: "Application", value: "app_name" },
        { text: "Last Occurrence", value: "last_occurrence" },
        { text: "Type", value: "type" },
        { text: "Category", value: "category" },
        { text: "Status", value: "status" },
        { text: "Count", value: "count" },
        { text: "Message", value: "message" },
      ],
    };
  },
  methods: {
    open(record) {
      this.selected = record;
      this.dialogs.show = true;
    },
    getAlerts() {
      this.loading = true;
      this.$api.alerts
        .listAlerts()
        .then((response) => {
          this.alerts = response.data;
          if (this.alertid) {
            for (let i = 0; i < this.alerts.length; i++) {
              const alert = this.alerts[i];
              if (alert.id === this.alertid) {
                this.open(alert);
                break;
              }
            }
          }
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
  mounted() {
    this.getAlerts();
  },
};
</script>


<style scoped>
input {
  width: 50px;
}
.v-text-field {
  padding: 10px 0px !important;
}
.v-data-table tr {
  cursor: pointer;
}
</style>
