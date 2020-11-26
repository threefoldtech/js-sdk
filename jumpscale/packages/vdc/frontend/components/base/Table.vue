<template>
  <div>
    <template>
      <v-data-table
        :loading="loading"
        :headers="headers"
        :items="deployedVdc"
        class="elevation-1"
      >
        <template slot="no-data">No VDC instances available</template>
        <template v-slot:item.id="{ item }">
          <div>{{ item.id }}</div>
        </template>
        <template v-slot:item.name="{ item }">
          <router-link :to="`/workloads/${item.vdc_name}`">{{
            item.vdc_name
          }}</router-link>
        </template>
        <template v-slot:item.package="{ item }">
          <div :class="`${item.class}`">{{ item.flavor }}</div>
        </template>
        <template v-slot:item.expiration="{ item }">
          <div :class="`${item.class}`">{{ item.expiration }}</div>
        </template>
        <template v-slot:item.actions="{ item }">
          <v-tooltip top>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon @click.stop="delete3Bot(item)">
                <v-icon v-bind="attrs" v-on="on" color="#810000"
                  >mdi-delete</v-icon
                >
              </v-btn>
            </template>
            <span>Destroy</span>
          </v-tooltip>
        </template>
      </v-data-table>
    </template>
    <cancel-workload
      v-if="selected"
      v-model="dialogs.cancelWorkload"
      :data="selected"
    ></cancel-workload>
  </div>
</template>

<script>
module.exports = {
  props: ["deployed", "headers", "loading"],
  components: {
    "cancel-workload": httpVueLoader("../solutions/Delete.vue"),
  },
  data() {
    return {
      dialogs: {
        cancelWorkload: false,
      },
      selected: null,
    };
  },
  methods: {
    delete3Bot(record) {
      this.selected = record;
      this.dialogs.cancelWorkload = true;
    },
  },
  computed: {
    deployedVdc() {
      return this.deployed.map((item, index) => ({
        id: index + 1,
        ...item,
      }));
    },
  },
};
</script>
