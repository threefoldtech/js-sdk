<template>
  <div>
    <v-card flat height="100%" class="pa-5" outlined>
      <v-card-text>
        <markdown-view
          base-url="https://legal.threefold.io/#/"
          url="https://raw.githubusercontent.com/threefoldfoundation/info_legal/development/wiki/terms_conditions_all.md"
        ></markdown-view>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="green darken-4" raised text @click="accept">Agree</v-btn>
        <v-btn color="red darken-4" raised text @click="showConfirmation = true"
          >Cancel</v-btn
        >
      </v-card-actions>
    </v-card>
    <v-dialog v-model="showConfirmation" persistent max-width="290">
      <v-card>
        <v-card-title class="headline">Confirmation</v-card-title>
        <v-card-text
          >You have chosen to disagree to Threefold's Terms and Conditions. You
          will be logged out. Are you sure?</v-card-text
        >
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="green darken-4" text @click="showConfirmation = false"
            >No</v-btn
          >
          <v-btn color="red darken-4" text @click.stop="logout">Yes</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="welcome_dialog" persistent max-width="500">
      <v-card>
        <v-card-title class="headline"> Welcome to ThreeFold Now </v-card-title>
        <v-card-text>
          This marketplace is a showcase of open source peer-to-peer apps built on top of the TF Grid. We are in demo mode
          and running on testnet. Note your deployment will be cancelled automatically after three hours.
          Forgive any instability you might encounter while our developers work out the kinks.
          <br />
          Please visit the
          <a href="https://manual.threefold.io/" target="_blank">manual</a> and <a href="https://now.threefold.io/" target="_blank">wiki</a> for
          more information.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="green darken-1" text @click="welcomeMessage = true">
            Ok
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
module.exports = {
  data() {
    return {
      showConfirmation: false,
      welcomeMessage: false,
    };
  },
  computed: {
    welcome_dialog() {
      return !this.welcomeMessage;
    },
  },
  methods: {
    accept: function (event) {
      this.$api.license.accept().then((result) => {
        this.$root.$emit("sidebar", true);
        this.$router.push({ path: "/" });
      });
    },
    logout() {
      // clear cache on logout
      var backlen = history.length;
      history.go(-backlen);
      window.location.href = "/auth/logout";
    }
  },
  mounted() {
    this.$root.$emit("sidebar", false);
  },
};
</script>
