<template>
  <div>
    <div class="actions mb-3">
      <h1 class="d-inline" color="primary" text>Wallet Information</h1>
      <v-btn
        v-if="wallet"
        class="float-right p-4"
        color="primary"
        text
        target="_blank"
        :href="`https://stellar.expert/explorer/public/account/${wallet.address}`"
      >
        <v-icon left>mdi-bank</v-icon>List transactions
      </v-btn>
    </div>
    <v-simple-table v-if="wallet && expirationdata">
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
                :color="
                  expirationdata.expiration_days < 2
                    ? 'error'
                    : expirationdata.expiration_days < 14
                    ? 'warning'
                    : 'primary'
                "
                v-for="(balance, i) in wallet.balances"
                :key="i"
              >
                {{ balance.balance }} {{ balance.asset_code }}
              </v-chip>
            </td>
          </tr>
          <tr>
            <td>VDC expiration date</td>
            <td class="ml-2">
              <p v-if="expirationdata.expiration_date">
                {{
                  new Date(
                    expirationdata.expiration_date * 1000
                  ).toLocaleString("en-GB")
                }}
              </p>
              <v-skeleton-loader
                v-else
                color="grey darken-2"
                class="pa-4 mb-6"
                :boilerplate="true"
                :elevation="2"
                type="text"
              ></v-skeleton-loader>
            </td>
          </tr>
          <tr>
            <td>QRCode</td>
            <td class="pt-1">
              <div class="text-left ma-1">
                <v-tooltip top>
                  <template v-slot:activator="{ on, attrs }">
                    <img
                      v-bind="attrs"
                      v-on="on"
                      style="border: 1px dashed #85929e"
                      :src="`data:image/png;base64, ${qrcode}`"
                    />
                  </template>
                  <span
                    >Scan the QRCode to topup wallet using Threefold Connect
                    application</span
                  >
                </v-tooltip>
              </div>
            </td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
    <v-skeleton-loader
      v-else
      color="grey darken-2"
      class="pa-4 mb-6"
      :boilerplate="true"
      :elevation="2"
      type="table-row-divider@6, article"
    ></v-skeleton-loader>
  </div>
</template>

<script>
module.exports = {
  props: {
    wallet: { type: Object, default: {} },
    expirationdata: { type: Object, default: {} },
    price: { type: Number, default: 100 },
  },
  mixins: [dialog],
  data() {
    return {
      showSecret: false,
      qrcode: "",
      qrcodeLoading: false,
    };
  },
  methods: {
    getQRCode() {
      this.qrcodeLoading = true;
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
  // Using Watchers should allow to update qrcode only when we have a wallet
  // and re-update it if the price or wallet value changes
  watch: {
    wallet(w) {
      w && this.getQRCode();
    },
    price() {
      this.wallet && this.getQRCode();
    },
  },
};
</script>
<style scoped>
h1 {
  color: #1b4f72;
}
</style>
