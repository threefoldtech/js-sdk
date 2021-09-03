<template>
  <base-dialog
    v-if="data"
    :title="title"
    v-model="dialog"
    :error="error"
    :info="info"
    :warning="warning"
    :loading="loading"
    :persistent="true"
  >
    <template #default>
      Please enter the password of <b class="font-weight-black">{{ data.name }}</b>. {{ messages.confirmationMsg }}
      <v-form @submit="submit">
        <v-text-field :type="'password'" v-model="form.password" dense></v-text-field>
      </v-form>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text color="error" @click="submit">Confirm</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  mixins: [dialog],
  data() {
    return {
      lastThreebotSelected: "",
    };
  },
  props:{
    title: String,
    api: String,
    data: Object,
    messages: Object,
  },
  methods: {
    submit() {
      if (!this.form.password) {
        this.error = "Password required";
      } else {
        this.loading = true;
        this.error = null;
        this.$api.solutions
          [this.api](this.data.solution_uuid, this.form.password)
          .then((response) => {
            this.alert(this.messages.successMsg, "success");
            this.$router.go(0);
          }).catch((err) => {
            this.error = err.response.data["error"];
            this.alert(this.error , "error");
            this.form.password = "";
          }).finally(() => {
            this.loading = false;
          });
      }
    },
  },
  updated() {
    if (this.lastThreebotSelected !== this.data.name) {
      this.warning = "";
      this.lastThreebotSelected = this.data.name;
    }
  },
};
</script>
