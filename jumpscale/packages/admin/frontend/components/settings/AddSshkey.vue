<template>
  <base-dialog
    title="Add SSH key"
    v-model="dialog"
    :error="error"
    :loading="loading"
  >
    <template #default>
        <v-file-input @change="readFile" prepend-icon="mdi-paperclip" label="File input" show-size outlined></v-file-input>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
      <v-btn text @click="submit">Add</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
    mixins: [dialog],
    data () {
      return {
        file: null,
        validators: {}
      }
    },
    methods: {
    readFile (file) {
        this.file = file
        const reader = new FileReader()
        reader.onload = (event) => {
            this.val = event.target.result
        }
        if (file) {
            reader.readAsText(file)
        }
    },
    submit() {
        this.error = null;
        console.log(this.val)
        if(!this.val){
            this.error = "SSH key file required"
        }
        else {
            this.$api.sshkeys.add(this.val)
            .then((response) => {
                this.done("SSH key added");
            })
            .catch((error) => {
                this.error = error.response.data.error;
            })
            .finally(() => {
                this.loading = false;
            });
        }
    },
  },
};
</script>
