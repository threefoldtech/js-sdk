<template>
  <div>
    <v-parallax :src="vdc_data.bg" height="100%">
      <v-row align="center" justify="center">
        <v-col class="text-center" cols="12">
          <h1 style="font-size: 60" class="mb-2">{{ vdc_data.header }}</h1>
          <h3 class="subheading">{{ vdc_data.subheader }}</h3>
          <v-btn
            color="#4472B5"
            class="mt-8 mx-2"
            dark
            large
            @click.stop="viewWorkloads()"
            >List VDCs</v-btn
          >

          <v-btn
            color="#7DB78D"
            class="mt-8 mx-2"
            dark
            large
            @click.stop="openChatflow('new_vdc')"
            >Deploy a VDC</v-btn
          >
        </v-col>
      </v-row>
    </v-parallax>
  </div>
</template>

<script>
module.exports = {
  data() {
    return {
      vdc_data: APPS["vdc"],
    };
  },
  methods: {
    openChatflow(topic) {
      this.$router.push({
        name: "SolutionChatflow",
        params: { topic: topic },
      });
    },
    viewWorkloads() {
      this.$router.push({ name: "Workloads" });
    },
  },
};
</script>
