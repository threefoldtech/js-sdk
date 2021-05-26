<template>
  <div>
    <!-- List-keys -->
    <base-section
      title="API Keys"
      icon="mdi-shield-key"
    >
      <template #actions>
        <v-btn text @click.stop="dialogs.generateKey = true">
          <v-icon left>mdi-plus</v-icon>Generate New Key
        </v-btn>
         <v-btn text @click.stop="deleteAll()" color="#810000" :disabled="keys.length === 0">
          <v-icon left color="#810000">mdi-delete color</v-icon>Invoke All Keys
        </v-btn>
      </template>

      <v-data-table
      :loading="loading"
      :headers="headers"
      :items="keys"
      :sort-by.sync="sortBy"
      class="elevation-1"
    >
      <template slot="no-data">No keys yet</template>
      <template v-slot:item.name="{ item }">
        <div>{{ item.name }}</div>
      </template>

      <template v-slot:item.role="{ item }">
        <div>{{ item.role }}</div>
      </template>

      <template v-slot:item.actions="{ item }">
        <v-tooltip top>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="editKey(item.name)">
              <v-icon v-bind="attrs" v-on="on" color="#1b4f72"
                >mdi-lead-pencil</v-icon
              >
            </v-btn>
          </template>
          <span>Edit</span>
        </v-tooltip>
        <v-tooltip top>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="regenerateKey(item.name)">
              <v-icon v-bind="attrs" v-on="on" color="#1b4f72"
                >mdi-reload</v-icon
              >
            </v-btn>
          </template>
          <span>Regenerate</span>
        </v-tooltip>
        <v-tooltip top>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="removeKey(item.name)">
              <v-icon v-bind="attrs" v-on="on" color="#810000"
                >mdi-delete</v-icon
              >
            </v-btn>
          </template>
          <span>Delete</span>
        </v-tooltip>

      </template>
    </v-data-table>

  <generate-key
    v-model="dialogs.generateKey"
    @done="list"
  ></generate-key>
  <edit-key
    v-if="selected"
    v-model="dialogs.editKey"
    :name="selected"
    @done="list"
  ></edit-key>
  <delete-key
    v-if="selected"
    v-model="dialogs.deleteKey"
    :name="selected"
    @done="list"
  ></delete-key>
  <delete-all-keys
    v-model="dialogs.deleteAllKeys"
    @done="list"
  ></delete-all-keys>
  <show-key
      v-model="dialogs.showKey"
      :apikey="apikey"
    ></show-key>
  </div>
</template>
<script>
module.exports = {
  mixins: [dialog],
  components: {
    "delete-key": httpVueLoader("./RemoveKey.vue"),
    "generate-key": httpVueLoader("./GenerateKey.vue"),
    "edit-key": httpVueLoader("./EditKey.vue"),
    "show-key": httpVueLoader("./ShowKey.vue"),
    "delete-all-keys": httpVueLoader("./DeleteAll.vue")
  },
  data() {
    return {
      selected: null,
      deleteAllKeys: null,
      apikey: null,
      sortBy: "name",
      dialogs: {
        actions: false,
        deleteKey: false,
        deleteAllKeys: false,
        generateKey: false,
        editKey: false,
        showKey: false,
      },
      keys: [],
      headers: [
        { text: "Name", value: "name" },
        { text: "Role", value: "role" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      loading: false,
    };
  },
  methods: {
    list() {
      this.loading = true;
      this.$api.apikeys
        .list()
        .then((response) => {
          this.keys = response.data.data;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    removeKey(name) {
      this.selected = name;
      this.dialogs.deleteKey = true;
    },
    deleteAll() {
      this.dialogs.deleteAllKeys = true;
    },
    editKey(name) {
      this.selected = name;
      this.dialogs.editKey = true;
    },
    regenerateKey(name) {
      this.loading = true;
      this.$api.apikeys
        .regenerate(name)
        .then((response) => {
          this.apikey = response.data.data.key;
          this.dialogs.showKey = true;
        })
        .catch((error) => {
          this.error = error.response.data;
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
  mounted() {
    this.list();
  },
};
</script>

<style scoped>
h1 {
  color: #1b4f72;
}

.v-input {
  width: 20%;
  margin-left: auto;
}
</style>
