<template>
  <div>
    <!-- List-keys -->
    <base-section
      title="API Keys"
      icon="mdi-shield-key"
    >
      <template #actions>
        <v-btn text @click.stop="generate()">
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
            <v-btn icon @click.stop="edit(item.name)">
              <v-icon v-bind="attrs" v-on="on" color="#1b4f72"
                >mdi-lead-pencil</v-icon
              >
            </v-btn>
          </template>
          <span>Edit</span>
        </v-tooltip>
        <v-tooltip top>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="regenerate(item.name)">
              <v-icon v-bind="attrs" v-on="on" color="#1b4f72"
                >mdi-reload</v-icon
              >
            </v-btn>
          </template>
          <span>Regenerate</span>
        </v-tooltip>
        <v-tooltip top>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click.stop="remove(item.name)">
              <v-icon v-bind="attrs" v-on="on" color="#810000"
                >mdi-delete</v-icon
              >
            </v-btn>
          </template>
          <span>Delete</span>
        </v-tooltip>

      </template>
    </v-data-table>

  <key-action
    v-model="dialogs.keyAction"
    :name="selected"
    :title="title"
    :message="message"
    :action="action"
    @done="list"
  ></key-action>
  </div>
</template>
<script>
module.exports = {
  mixins: [dialog],
  components: {
    "key-action": httpVueLoader("./ApiKeyActions.vue"),
  },
  data() {
    return {
      selected: null,
      sortBy: "name",
      loading: false,
      message: null,
      title: null,
      dialogs: {
        keyAction: false,
      },
      action: {
        name: null,
        buttonName: null,
      },
      keys: [],
      headers: [
        { text: "Name", value: "name" },
        { text: "Role", value: "role" },
        { text: "Actions", value: "actions", sortable: false },
      ],
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
    generate() {
      this.dialogs.keyAction = true;
      this.title = "Generate Key";
      this.message = "Please specify key name and its role";
      this.action.name = "generate";
      this.action.buttonName = "Generate";
    },
    regenerate(name) {
      this.selected = name;
      this.dialogs.keyAction = true;
      this.title = "Regenerate Key";
      this.message = `Are you sure you want to regenerate this key ${name}?  be aware that any scripts or applications using this key will need to be updated.`;
      this.action.name = "regenerate";
      this.action.buttonName = "Confirm";
    },
    edit(name) {
      this.selected = name;
      this.dialogs.keyAction = true;
      this.title = "Edit Key Role";
      this.message = `Please specify a role for key ${name}`;
      this.action.name = "edit";
      this.action.buttonName = "Submit";
    },
    remove(name) {
      this.selected = name;
      this.dialogs.keyAction = true;
      this.title = "Remove Key";
      this.message = `Are you sure you want to remove ${name} from API Keys`;
      this.action.name = "delete";
      this.action.buttonName = "Confirm";
    },
    deleteAll() {
      this.dialogs.keyAction = true;
      this.title = "Remove All Keys";
      this.message = "Are you sure you want to remove all API Keys?";
      this.action.name = "deleteAll";
      this.action.buttonName = "Confirm";
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
