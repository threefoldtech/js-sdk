<template>
  <base-dialog title="Generated Key" v-model="dialog" textcolor="indigo">
    <template #default>
      <p class="font-weight-black">
        Make sure to copy your new key now. You won’t be able to see it again!
        <br />
      </p>
      <v-text-field
        :value="apikey"
        readonly
        filled
        dense
        outlined
        color="indigo"
        :append-icon="copyicon"
        @click:append="copyText"
      ></v-text-field>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  mixins: [dialog],
  props: ["apikey"],
  data() {
    return {
      copyicon: "mdi-content-copy",
    };
  },
  methods: {
    copyText() {
      const elem = document.createElement("textarea");
      elem.value = this.apikey;
      elem.textContent = this.apikey;
      document.body.appendChild(elem);
      var selection = document.getSelection();
      var range = document.createRange();
      range.selectNode(elem);
      selection.removeAllRanges();
      selection.addRange(range);
      document.execCommand("copy");
      this.copyicon = "mdi-check";
      setTimeout(() => {
        this.copyicon = "mdi-content-copy";
      }, 1000);
      selection.removeAllRanges();

      document.body.removeChild(elem);
    },
  },
};
</script>
