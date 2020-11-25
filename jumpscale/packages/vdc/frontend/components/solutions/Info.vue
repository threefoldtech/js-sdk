<template>
  <div>
    <base-dialog :title="title" v-model="dialog" :loading="loading">
      <template #default>
        <v-tabs v-model="tab" background-color="transparent" color="basil" grow>
          <v-tab-item :key="'moredetails'">
            <v-card flat>
              <json-tree :raw="JSON.stringify(json)"></json-tree>
            </v-card>
          </v-tab-item>
        </v-tabs>
      </template>
      <template #actions>
        <v-btn
          v-if="data.Name !== undefined"
          text
          color="error"
          @click.stop="cancel()"
          >Delete Reservation</v-btn
        >
        <v-btn text @click="close">Close</v-btn>
      </template>
    </base-dialog>
    <cancel-solution
      v-model="dialogs.cancelSolution"
      :data="data"
    ></cancel-solution>
  </div>
</template>

<script>
module.exports = {
  components: {
    "cancel-solution": httpVueLoader("./Delete.vue"),
  },
  data() {
    return {
      dialogs: {
        cancelSolution: false,
      },
      tab: 0,
    };
  },
  props: { data: Object },
  mixins: [dialog],
  computed: {
    json() {
      delete this.data["class"];
      return this.data;
    },
    title() {
      return this.data.Name === undefined
        ? "Workload details"
        : "Solution details";
    },
    KeysWithTypeList() {
      return ["Node ids", "wids", "Active workload ids"];
    },
  },
  methods: {
    cancel() {
      this.dialogs.cancelSolution = true;
    },
  },
};
</script>
