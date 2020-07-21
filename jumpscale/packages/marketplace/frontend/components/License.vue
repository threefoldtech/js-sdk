<template>
  <div>
    <v-card flat height="100%" class="pa-5" outlined>
      <v-card-title class="justify-center">Terms and Conditions for using Threefold Marketplace</v-card-title>
      <v-card-text>
        Contrary to popular belief, Lorem Ipsum is not simply random text.
        It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old.
        Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words,
        consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature,
        discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum"
        (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics,
        very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..",
        comes from a line in section 1.10.32.
        The standard chunk of Lorem Ipsum used since the 1500s is reproduced below for those interested.
        Sections 1.10.32 and 1.10.33 from "de Finibus Bonorum et Malorum" by Cicero are also reproduced in their exact original form,
        accompanied by English versions from the 1914 translation by H. Rackham.
        Contrary to popular belief, Lorem Ipsum is not simply random text.
        It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old.
        Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words,
        consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature,
        discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum"
        (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics,
        very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..",
        comes from a line in section 1.10.32.
        The standard chunk of Lorem Ipsum used since the 1500s is reproduced below for those interested.
        Sections 1.10.32 and 1.10.33 from "de Finibus Bonorum et Malorum" by Cicero are also reproduced in their exact original form,
        accompanied by English versions from the 1914 translation by H. Rackham.
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
