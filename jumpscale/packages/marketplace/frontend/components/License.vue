<template>
  <div>
    <v-card flat height="100%" class="pa-5" outlined>
      <v-card-title class="justify-center">Terms and Conditions for using Threefold Marketplace</v-card-title>
      <v-card-text>
        It's very important that you as a Marketplace user you agree to the
        <a
          href="http://decentralization2.threefold.io/"
          target="_blank"
        >Decentralization Manifesto.</a>
        Please check here: for the terms and conditions.
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
        <v-card-title class="headline">Confirmirmation</v-card-title>
        <v-card-text>You choose not to agree to the terms and conditions, You will be logged out. Are you sure?</v-card-text>
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
    accept: function (event) {
      this.$api.license.accept().then((result) => {
        this.$root.$emit("sidebar", true);
        this.$router.push({ path: "/" });
      });
    },
  },
  data() {
    return { showConfirmation: false };
  },
  mounted() {
    this.$root.$emit("sidebar", false);
  },
};
</script>
