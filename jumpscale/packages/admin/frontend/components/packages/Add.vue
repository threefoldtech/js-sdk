<template>
  <base-dialog title="Add New Package" v-model="dialog" :error="error" :loading="loading">
    <template #default>
      <v-form>
        <v-text-field v-model="form.path" label="Path" dense></v-text-field>
        <v-text-field v-model="form.giturl" label="Git url" dense></v-text-field>

        <v-row class="my-0 py-0" v-for="(item, key, index) in form.extras" :key="index">
          <v-col class="my-0 py-0" cols="12" md="4">
            <v-text-field :value="key" solo flat dense readonly></v-text-field>
          </v-col>
          <v-col class="my-0 py-0" cols="12" md="4">
            <v-text-field :value="item" solo flat dense readonly></v-text-field>
          </v-col>
          <v-col class="my-0 py-0" cols="12" md="4">
            <v-btn icon @click="remove(key)" color="primary">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </v-col>
        </v-row>
        <v-row>
          <v-subheader><strong> Package Parameters </strong></v-subheader>
          <v-tooltip v-model="show" top>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon v-bind="attrs" v-on="on">
                <v-icon color="grey lighten-1"> mdi-help-circle </v-icon>
              </v-btn>
            </template>
            <span>If the package requires extra parameters during installation
              provide it in the following fields</span>
          </v-tooltip>
        </v-row>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field v-model="k" label="Key" dense required></v-text-field>
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field v-model="v" label="Value" dense required></v-text-field>
          </v-col>
          <v-col cols="12" md="4">
            <v-btn icon @click="add" color="primary">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text @click="submit">Submit</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  mixins: [dialog],
  data() {
    return {
      form: { extras: {} },
      k: null,
      v: null,
      show: null
    };
  },
  methods: {
    submit() {
      this.loading = true;
      this.error = null;
      this.$api.packages
        .add(this.form.path, this.form.giturl, this.form.extras)
        .then(response => {
          this.done("Package is added");
        })
        .catch(error => {
          this.error = error.response.data.error
        })
        .finally(() => {
          this.loading = false;
        });
    },
    add() {
      if (this.k && this.v) {
        this.$set(this.form.extras, this.k, this.v);
        this.reset();
      }
    },
    reset() {
      this.k = null;
      this.v = null;
    },
    remove(k) {
      this.$delete(this.form.extras, k);
    }
  }
};
</script>
