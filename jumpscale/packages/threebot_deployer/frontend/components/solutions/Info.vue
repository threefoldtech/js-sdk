<template>
  <div>
    <base-dialog :title="title" v-model="dialog" :loading="loading">
      <template #default>
        <v-tabs v-model="tab" background-color="transparent" color="basil" grow>
          <v-tab :key="title">{{ title }}</v-tab>
          <v-tab :key="'moredetails'">More details</v-tab>

          <v-tab-item :key="title">
            <v-simple-table>
              <template v-slot:default>
                <tbody>
                  <tr>
                    <th>Workload IDs</th>
                    <td class="pt-2">
                      <v-chip
                        class="ma-1"
                        v-for="node in json['wids']"
                        :key="node"
                        >{{ node }}</v-chip
                      >
                    </td>
                  </tr>
                  <tr>
                    <th>3Bot Name</th>
                    <td>{{ json["name"] }}</td>
                  </tr>
                  <tr>
                    <th>State</th>
                    <td>{{ json["state"] }}</td>
                  </tr>
                  <tr>
                    <th>Domain</th>
                    <td
                      v-if="
                        json['state'] === 'RUNNING' || json['state'] === 'ERROR'
                      "
                    >
                      <a
                        :href="`https://${json['domain']}/admin`"
                        target="_blank"
                      >
                        {{ json["domain"] }}
                      </a>
                    </td>
                    <td v-else>{{ json["domain"] }}</td>
                  </tr>
                  <tr
                    v-if="
                      json['state'] === 'RUNNING' || json['state'] === 'ERROR'
                    "
                  >
                    <th>IPv4 Address</th>
                    <td>{{ json["ipv4"] }}</td>
                  </tr>
                  <tr>
                    <th>Network</th>
                    <td>{{ json["network"] }}</td>
                  </tr>
                  <tr
                    v-if="
                      json['state'] === 'RUNNING' || json['state'] === 'ERROR'
                    "
                  >
                    <th>IPv6 Address</th>
                    <td>{{ json["ipv6"] }}</td>
                  </tr>
                  <tr>
                    <th>CPU</th>
                    <td>{{ json["cpu"] }}</td>
                  </tr>
                  <tr>
                    <th>Memory</th>
                    <td>{{ json["memory"] }}</td>
                  </tr>
                  <tr>
                    <th>Disk Size</th>
                    <td>{{ json["disk_size"] }}</td>
                  </tr>
                  <tr>
                    <th>Farm</th>
                    <td>{{ json["farm"] }}</td>
                  </tr>
                  <tr>
                    <th>Continent</th>
                    <td>{{ json["continent"] }}</td>
                  </tr>
                  <tr>
                    <th>Node ID</th>
                    <td>{{ json["node"] }}</td>
                  </tr>
                  <tr v-if="json['state'] === 'RUNNING'">
                    <th>Expiration</th>
                    <td>{{ json["expiration"] }}</td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
          </v-tab-item>
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
