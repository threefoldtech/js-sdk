<template>
  <div>
    <base-dialog :title="title" v-model="dialog" :loading="loading">
      <template #default>
        <v-list-item v-for="(item, key)  in json" :key="key">
          <v-list-item-content v-if="key === 'nodes'">
            <v-list-item-title v-text="key"></v-list-item-title>
            <v-list-item v-for="(node, key)  in item" :key="key">
              <v-list-item-title v-text="node"></v-list-item-title>
              <v-list-item-subtitle v-text="key"></v-list-item-subtitle>
            </v-list-item>
          </v-list-item-content>
          <v-list-item-content v-else-if="key === 'node_ids' ||key === 'active_workload_ids'">
            <v-list-group :key="key" no-action>
              <v-list-tile slot="activator">
                <v-list-tile-content>
                  <v-list-tile-title>{{ key }}</v-list-tile-title>
                </v-list-tile-content>
              </v-list-tile>
              <v-list-tile v-for="node in item" :key="node">
                <v-list-tile-content>
                  <v-list-item-subtitle v-text="`- ${node}`"></v-list-item-subtitle>
                </v-list-tile-content>
              </v-list-tile>
            </v-list-group>
          </v-list-item-content>
          <v-list-item-content v-else>
            <v-list-item-title v-text="key"></v-list-item-title>
            <v-list-item-subtitle v-text="item"></v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <!-- <code-area mode="python" :content="json"></code-area> -->
      </template>
      <template #actions>
        <v-btn
          v-if="data.Name !== undefined"
          text
          color="error"
          @click.stop="cancel()"
        >Delete Reservation</v-btn>
        <v-btn text @click="close">Close</v-btn>
      </template>
    </base-dialog>
    <cancel-solution v-model="dialogs.cancelSolution" :wids="data.wids"></cancel-solution>
  </div>
</template>

<script>
module.exports = {
  components: {
    "cancel-solution": httpVueLoader("./CancelSolution.vue"),
  },
  props: { data: Object },
  mixins: [dialog],
  data() {
    return {
      dialogs: {
        cancelSolution: false,
      },
    };
  },
  computed: {
    json() {
      console.log(this.data);
      if (this.data.last_updated !== undefined)
        this.data.last_updated = new Date(this.data.last_updated * 1000);
      if (this.data.empty_at !== undefined)
        this.data.empty_at = new Date(this.data.empty_at * 1000);
      return this.data;
    },
    title() {
      return this.data.Name === undefined
        ? "Workload details"
        : "Solution details";
    },
  },
  methods: {
    cancel() {
      this.dialogs.cancelSolution = true;
    },
  },
};
</script>
