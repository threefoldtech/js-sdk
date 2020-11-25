<template>
  <div>
    <base-component title="Logs" icon="mdi-text" :loading="loading">
      <template #actions>
        <v-btn color="primary" text @click.stop="dialogs.delete = true">
          <v-icon left>mdi-delete-sweep</v-icon> Delete
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
        <v-data-table :loading="loading" :search="search" :headers="headers" :items="data"  :sort-by="['id', 'epoch']" :sort-desc="[true, true]"@click:row="open" class="elevation-1">
          <template slot="no-data">No logs available</p></template>
          <template v-slot:item.message="{ item }">
            {{ item.message.slice(0, 50) }} {{ item.message.length > 50 ? '...' : ''}}
          </template>

          <template v-slot:item.epoch="{ item }">
            {{ new Date(item.epoch * 1000).toLocaleString('en-GB') }}
          </template>

          <template v-slot:item.level="{ item }">
            <v-chip dark :color="levels[item.level].color">{{ levels[item.level].text }}</v-chip>
          </template>

          <template v-slot:body.prepend="{ headers }">
            <tr>
              <td>
                <v-text-field v-model="filters.id" clearable filled hide-details dense></v-text-field>
              </td>
              <td>
                <v-select v-model="appname" :items="apps" @change="getLogs" filled hide-details dense></v-select>
              </td>
              <td></td>
              <td>
                <v-text-field v-model="filters.category" clearable filled hide-details dense></v-text-field>
              </td>
              <td>
                <v-select v-model="filters.level" :items="Object.values(levels)" clearable filled hide-details dense></v-select>
              </td>
              <td>
                <v-select v-model="filters.module" :items="modules" clearable filled hide-details dense></v-select>
              </td>
              <td>
                <v-text-field v-model="filters.context" clearable filled hide-details dense></v-text-field>
              </td>
              <td>
                <v-text-field v-model="filters.message" clearable filled hide-details dense></v-text-field>
              </td>
              <td>
                <v-text-field v-model="filters.processid" clearable filled hide-details dense></v-text-field>
              </td>
            </tr>
          </template>
        </v-data-table>
      </template>
    </base-component>

    <show-record v-if="selected" v-model="dialogs.show" :record="selected"></show-record>
    <delete-record v-if="appname" v-model="dialogs.delete" :appname="appname" @done="getLogs"></delete-record>

  </div>
</template>

<script>
module.exports = {
  components: {
    "show-record": httpVueLoader("./Log.vue"),
    "delete-record": httpVueLoader("./Delete.vue"),
  },
  data() {
    return {
      appname: "gedis",
      search: "",
      apps: [],
      logs: [],
      modules: [],
      dialogs: {
        show: false,
        delete: false,
      },
      selected: null,
      loading: false,
      levels: LEVELS,
      filters: {
        id: null,
        epoch: null,
        category: null,
        level: null,
        module: null,
        context: null,
        message: null,
        processid: null,
      },
      headers: [
        { text: "Id", value: "id" },
        { text: "Application", value: "app_name" },
        { text: "Timestamp", value: "epoch" },
        { text: "Category", value: "category" },
        { text: "Level", value: "level" },
        { text: "Module", value: "module" },
        { text: "Context", value: "context" },
        { text: "Message", value: "message" },
        { text: "Process Id", value: "processid" },
      ],
    };
  },
  computed: {
    data() {
      return this.logs.filter((record) => {
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
    getApps() {
      this.$api.logs.listApps().then((response) => {
        this.apps = JSON.parse(response.data).data;
      });
    },
    getLogs() {
      this.loading = true;
      this.$api.logs
        .listLogs(this.appname)
        .then((response) => {
          this.logs = JSON.parse(response.data).data;
          this.modules = this.logs
            .filter((record) => record.module)
            .map((record) => record.module);
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
  mounted() {
    this.getApps();
    this.getLogs();
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
