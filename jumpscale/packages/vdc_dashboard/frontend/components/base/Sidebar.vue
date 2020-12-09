<template>
  <v-card width="256">
    <v-navigation-drawer permanent>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="title">
            <v-dialog v-model="dialog" persistent max-width="500">
              <template v-slot:activator="{ on, attrs }">
                <v-btn v-bind="attrs" v-on="on">
                  <v-icon left color="primary">mdi-wallet</v-icon> {{ name }}
                </v-btn>
              </template>
              <v-card>
                <v-card-title class="headline"> </v-card-title>
                <v-card-text
                  >Please send TFT tokens to this wallet to fund your vdc.
                  <br />
                  <br />
                  <span class="mr-2">Address: {{ address }}</span>
                  <v-tooltip top>
                    <template v-slot:activator="{ on, attrs }">
                      <v-icon
                        left
                        color="primary"
                        v-bind="attrs"
                        v-on="on"
                        @click.stop.prevent="copy"
                        >mdi-content-copy</v-icon
                      ><input type="hidden" id="copy-text" :value="address" />
                    </template>
                    <span>Copy</span>
                  </v-tooltip>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn color="red darken-1" text @click="dialog = false">
                    Close
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>

      <v-list dense nav>
        <v-list-item
          link
          @click="setActive(1)"
          :class="{ active: activeIndex == 1 }"
        >
          <v-list-item-content>
            <v-list-item-title class="text-capitalize">
              <router-link class="d-block" :to="`/kubernetes`">
                kubernetes</router-link
              >
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item
          link
          @click="setActive(2)"
          :class="{ active: activeIndex == 2 }"
        >
          <v-list-item-content>
            <v-list-item-title class="text-capitalize">
              <router-link class="d-block" :to="`/s3`"> s3</router-link>
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
  </v-card>
</template>

<script>
module.exports = {
  name: "Sidebar",
  props: {
    name: String,
    address: {
      type: String,
      default: "Wallet Address",
    },
  },
  data() {
    return {
      activeIndex: 1,
      dialog: false,
    };
  },
  methods: {
    setActive(index) {
      this.activeIndex = index;
    },
    copy() {
      let testingCodeToCopy = document.querySelector("#copy-text");
      testingCodeToCopy.setAttribute("type", "text");
      testingCodeToCopy.select();
      let successful = document.execCommand("copy");
      testingCodeToCopy.setAttribute("type", "hidden");
      window.getSelection().removeAllRanges();
    },
  },
};
</script>

<style scoped>
.v-list-item__title a {
  text-decoration: none;
  font-size: 1rem;
  padding: 5px 10px;
}

.active {
  background-color: #1b4f72;
}

.active .v-list-item__title a {
  color: #fff;
}

.v-list--nav .v-list-item {
  border-radius: 0;
}

.v-list--nav {
  padding: 0;
}

.v-btn__content {
  text-transform: initial;
}

.theme--light.v-btn:not(.v-btn--flat):not(.v-btn--text):not(.v-btn--outlined) {
  background-color: transparent;
}

.v-btn--contained {
  box-shadow: none;
}
.v-btn:not(.v-btn--text):not(.v-btn--outlined):hover:before {
  opacity: 0;
}
:focus {
  outline: transparent;
}
</style>
