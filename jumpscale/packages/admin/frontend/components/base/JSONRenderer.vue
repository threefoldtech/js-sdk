<template>
  <div>
    <v-tabs v-model="tab" background-color="transparent" color="basil" grow>
      <v-tab :key="title">{{ title }}</v-tab>
      <v-tab :key="'moredetails'">More Details</v-tab>

      <v-tab-item :key="title">
        <v-simple-table>
          <template v-slot:default>
            <tbody>
              <tr v-for="(item, key) in jsonobj" :key="key">
                <th v-if="!ignored.includes(key) && item !== ''">{{ key }}</th>
                <td v-if="typelist.includes(key)" class="pt-2">
                  <v-chip class="ma-1" v-for="node in item" :key="node">{{
                    node
                  }}</v-chip>
                </td>
                <td v-else-if="typedict.includes(key)" class="pt-2">
                  <v-chip
                    class="ma-1"
                    v-for="(subItem, subkey) in item"
                    :key="subkey"
                    >{{ subkey }} : {{ subItem }}</v-chip
                  >
                </td>
                <td v-else-if="!ignored.includes(key) && item !== ''">
                  {{ item }}
                </td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </v-tab-item>
      <v-tab-item :key="'moredetails'">
        <v-card flat>
          <json-tree :raw="JSON.stringify(jsonobj)" id="test"></json-tree>
        </v-card>
      </v-tab-item>
    </v-tabs>
    <v-btn
      v-if="tab === 1"
      color="#52BE80"
      class="copy-btn ma-2 white--text"
      fab
      @click="copyjson()"
    >
      <v-icon dark> mdi-content-copy </v-icon>
    </v-btn>
  </div>
</template>

<script>
module.exports = {
  data() {
    return {
      tab: 0,
      lastObj: null,
    };
  },
  props: {
    title: String,
    jsonobj: {
      type: Object,
      default: () => ({}),
    },
    ignored: { type: Array, default: () => [] },
    typelist: { type: Array, default: () => [] },
    typedict: { type: Array, default: () => [] },
  },
  methods: {
    copyjson() {
      const elem = document.createElement("textarea");
      elem.value = JSON.stringify(this.jsonobj);
      document.body.appendChild(elem);
      elem.select();
      document.execCommand("copy");
      document.body.removeChild(elem);
      this.alert("copied", "success");
    },
  },
  updated() {
    if (this.jsonobj !== this.lastObj) this.tab = 0;
    this.lastObj = this.jsonobj;
  },
  mounted() {
    this.lastObj = this.jsonobj;
  },
};
</script>


<style>
.copy-btn {
  position: absolute;
  right: 10;
  top: 10;
}
</style>
