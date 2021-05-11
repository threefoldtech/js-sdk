<template>
  <div>
    <base-dialog :title="title" v-model="dialog" :loading="loading">
      <template #default>
        <json-renderer
          :title="title"
          :jsonobj="json"
          :typelist="KeysWithTypeList"
          :typedict="KeysWithTypeDict"
        ></json-renderer>
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
      KeysWithTypeList: ["Node ids", "wids", "Active workload ids","IPv4 Address(es)", "IPv6 Address(es)","Node(s)"],
      KeysWithTypeDict: ["nodes", "Volumes"]
    };
  },
  computed: {
    json() {
      if (this.data["Last updated"] !== undefined)
        this.data["Last updated"] = new Date(this.data["Last updated"] * 1000);
      if (this.data["Empty at"] !== undefined)
        this.data["Empty at"] = new Date(this.data["Empty at"] * 1000);
      if (this.data.Volumes !== undefined)
        this.data.Volumes = this.data.Volumes[0]
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
