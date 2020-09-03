<template>
  <div>
    <v-card flat height="100%" class="pa-5" outlined>
      <v-card-title class="justify-center">TF Grid Usage's Terms and Conditions</v-card-title>
      <v-card-text>
        Before using 3Bot Deployer and the TF Grid, you are obligated to agree to Threefold's
        <a
          target="_blank"
          href="https://wiki.threefold.io/#/terms_conditions"
        >Terms and Conditions.</a>. 
        Once agreed, please check
        <a
          target="_blank"
          href="https://manual-testnet.threefold.io/#/getting_started"
        >pre-requisites</a>
        to get started quickly.
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="green darken-4" raised text @click="accept">Agree</v-btn>
        <v-btn color="red darken-4" raised text @click="showConfirmation=true">Cancel</v-btn>
      </v-card-actions>
    </v-card>
    <v-dialog v-model="showConfirmation" persistent max-width="290">
      <v-card>
        <v-card-title class="headline">Confirmation</v-card-title>
        <v-card-text>You have chosen to disagree to Threefold's Terms and Conditions. You will be logged out. Are you sure?</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="green darken-4" text @click="showConfirmation = false">No</v-btn>
          <v-btn color="red darken-4" text href="/auth/logout">Yes</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
module.exports = {
  methods: {
    accept: function(event) {
      this.$api.license.accept().then(result => {
        this.$root.$emit("sidebar", true);
        this.$router.push({ path: "/" });
      });
    }
  },
  data() {
    return { showConfirmation: false };
  },
  mounted() {
    this.$root.$emit("sidebar", false);
  }
};
</script>
