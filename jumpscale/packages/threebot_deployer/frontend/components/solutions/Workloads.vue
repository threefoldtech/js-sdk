<template>
  <div>
    <base-component title="MY WORKLOADS" icon="mdi-clipboard-list-outline" :loading="loading">
      <template #actions>
        <v-btn color="primary" text @click.stop="openChatflow()">
          <v-icon left>mdi-plus</v-icon> New
        </v-btn>
      </template>

      <template #default>
        <v-data-table :loading="loading" :headers="headers" :items="deployedSolutions" @click:row="open" class="elevation-1">
            <template v-slot:item.actions="{ item }">
                <v-icon small class="mr-2" @click="goto(item.Domain)">
                    mdi-web
                </v-icon>
            </template>
        </v-data-table>
      </template>
    </base-component>
    <solution-info v-if="selected" v-model="dialogs.info" :data="selected"></solution-info>
  </div>
</template>

<script>
  module.exports = {
    components: {
      "solution-info": httpVueLoader("./Info.vue"),
    },
    data () {
      return {
        threebot_data: APPS["threebot"],
        dialogs: {
          info: false,
        },
        selected: null,
        loading: true,
        headers: [
          {text: "Name", value: "Name"},
          {text: "Domain", value: "Domain"},
          {text: "Pool", value: "Pool"},
          {text: "Network", value: "Network"},
          {text: 'Actions', value: 'actions', sortable: false },
        ],
        deployedSolutions: [],
      }
    },
    methods: {
        open (record) {
            this.selected = record
            this.dialogs.info = true
        },
        openChatflow() {
            this.$router.push({
            name: "SolutionChatflow",
            params: { topic: this.threebot_data.type },
            });
        },
        getDeployedSolutions() {
            this.$api.solutions.getDeployed().then((response) => {
                this.deployedSolutions = [...response.data.data];
            }).finally(() => {
                this.loading = false;
            });
        },
        goto(domain) {
            // TODO:
        }
    },
    mounted () {
      this.getDeployedSolutions()
    }
  }
</script>
