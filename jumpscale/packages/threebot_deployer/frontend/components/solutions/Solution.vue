<template>
  <div>
    <v-parallax :src="threebot_data.bg" height="100%">
      <v-row align="center" justify="center">
        <v-col class="text-center" cols="12">
          <h1 style="font-size: 60;" class="mb-2">{{threebot_data.header}}</h1>
          <h3 class="subheading">{{threebot_data.subheader}}</h3>
          <v-btn color="#7DB78D" class="mt-8 mx-2" dark large @click.stop="openChatflow()">Deploy a new 3Bot</v-btn>
          <v-btn color="#4472B5" class="mt-8 mx-2" dark large @click.stop="viewWorkloads()">View my existing 3Bots</v-btn>
        </v-col>
      </v-row>
    </v-parallax>
  </div>
</template>

<script>
module.exports = {
  data() {
    return {
      threebot_data: APPS["threebot"],
    };
  },
  methods: {
    openChatflow() {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: this.threebot_data.type },
      });
    },
    viewWorkloads() {
        this.$router.push({name: "Workloads"});
      },
  },
};
</script>
