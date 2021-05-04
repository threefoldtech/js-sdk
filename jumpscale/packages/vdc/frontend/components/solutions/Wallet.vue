<template>
  <base-dialog title="Wallet details" v-model="dialog" :loading="loading">
    <template #default>
      <v-simple-table v-if="wallet">
        <template v-slot:default>
          <tbody>
            <tr>
              <td>Network</td>
              <td>{{ wallet.network }}</td>
            </tr>
            <tr>
              <td>Address</td>
              <td>{{ wallet.address }}</td>
            </tr>
            <tr>
              <td>Secret</td>
              <td>
                <v-text-field
                  hide-details
                  :value="wallet.secret"
                  readonly
                  solo
                  flat
                  :append-icon="showSecret ? 'mdi-eye' : 'mdi-eye-off'"
                  :type="showSecret ? 'text' : 'password'"
                  @click:append="showSecret = !showSecret"
                ></v-text-field>
              </td>
            </tr>
            <tr>
              <td>Balance</td>
              <td class="pt-1">
                <v-chip
                  outlined
                  class="ma-2"
                  v-for="(balance, i) in wallet.balances"
                  :key="i"
                >
                  {{ balance.balance }} {{ balance.asset_code }}
                </v-chip>
              </td>
            </tr>
            <tr>
              <td>QRCode</td>
              <td class="pt-1">
                <v-tooltip top>
                  <template v-slot:activator="{ on, attrs }">
                    <div class="text-left ma-4" v-bind="attrs" v-on="on">
                      <img
                        style="border: 1px dashed #85929e"
                        :src="`data:image/png;base64, ${qrcode}`"
                      />
                    </div>
                  </template>
                  <span
                    >Scan the QRCode to topup wallet using Threefold Connect
                    application</span
                  >
                </v-tooltip>
              </td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </template>
    <template #actions>
      <v-btn text @click="close">Close</v-btn>
    </template>
  </base-dialog>
</template>

<script>
module.exports = {
  props: ["vdcname"],
  mixins: [dialog],
  data() {
    return {
      wallet: null,
      price: null,
      showSecret: false,
      qrcode: "",
      lastVdcName: "",
    };
  },

  methods: {
    getVdcInfo() {
      this.loading = true;
      this.$api.solutions
        .getVdcInfo(this.vdcname)
        .then((response) => {
          this.wallet = response.data.wallet;
          this.price = response.data.price;
          this.lastVdcName = this.vdcname;
          this.getQRCode();
        })
        .catch((err) => {
          console.log(err);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    getQRCode() {
      this.$api.wallets
        .walletQRCodeImage(this.wallet.address, this.price, 3)
        .then((result) => {
          this.qrcode = result.data.data;
        })
        .catch((err) => {
          console.log(err);
        });
    },
  },
  mounted() {
    this.getVdcInfo();
  },
  updated() {
    if (this.wallet && !this.loading && this.lastVdcName !== this.vdcname) {
      this.wallet = null;
      this.getVdcInfo();
    }
  },
};
</script>
