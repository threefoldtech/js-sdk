<template>
  <div>
    <base-component title="Alerts" icon="mdi-alert-outline" :loading="loading">
      <template #actions>
        <v-btn color="primary" text @click.stop="dialogs.delete = true">
          <v-icon left>mdi-delete-sweep</v-icon> Delete All
        </v-btn>
      </template>

      <template #default>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field>
        <v-data-table class="elevation-1" :loading="loading" :search="search" :headers="headers" :items="data" @click:row="open"  :sort-by="['id']" :sort-desc="[true]" :page.sync="page">
          <template slot="no-data">No Alerts available</p></template>
          <template v-slot:item.message="{ item }">
            {{ item.message.slice(0, 50) }} {{ item.message.length > 50 ? '...' : ''}}
           </template>

           <template v-slot:item.last_occurrence="{ item }">
            {{ new Date(item.last_occurrence * 1000).toLocaleString('en-GB') }}
          </template>

          <template v-slot:body.prepend="{ headers }">
          <tr>
            <td>
              <v-text-field v-model="filters.id" clearable filled hide-details dense></v-text-field>
            </td>
            <td>
              <v-select v-model="filters.appname" :items="apps" clearable filled hide-details dense></v-select>
            </td>
            <td></td>
            <td>
              <v-select v-model="filters.type" :items="types" clearable filled hide-details dense></v-select>
            </td>
            <td>
              <v-text-field v-model="filters.category" clearable filled hide-details dense></v-text-field>
            </td>
            <td>
              <v-select v-model="filters.status" :items="states" clearable filled hide-details dense></v-select>
            </td>
            <td>
              <v-text-field v-model="filters.count" clearable filled hide-details dense></v-text-field>
            </td>
            <td>
              <v-text-field v-model="filters.message" clearable filled hide-details dense></v-text-field>
            </td>
          </tr>
        </template>

        </v-data-table>
      </template>
    </base-component>

    <show-alert v-if="selected" v-model="dialogs.show" :alertdata="selected"></show-alert>
  </div>
</template>


<script>
module.exports = {
  components: {
    "show-alert": httpVueLoader("./Alert.vue"),
  },
  data() {
    return {
      search: "",
      apps: [],
      alerts: [],
      selected: null,
      page: 1,
      dialogs: {
        show: false,
      },
      loading: false,
      levels: LEVELS,
      types: TYPES,
      states: STATES,
      filters: {
        id: null,
        appname: null,
        type: null,
        category: null,
        status: null,
        count: null,
        message: null,
      },
      headers: [
        { text: "Id", value: "id" },
        { text: "Application", value: "appname" },
        { text: "Last Occurrence", value: "last_occurrence" },
        { text: "Type", value: "type" },
        { text: "Category", value: "category" },
        { text: "Status", value: "status" },
        { text: "Count", value: "count" },
        { text: "Message", value: "message" },
      ],
    };
  },
  computed: {
    data() {
      return this.alerts.filter((record) => {
        let result = [];
        Object.keys(this.filters).forEach((key) => {
          result.push(
            !this.filters[key] ||
              String(record[key]).includes(this.filters[key])
          );
        });
        return result.every(Boolean);
      });
    },
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
          this.alerts = JSON.parse(response.data).data;
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
