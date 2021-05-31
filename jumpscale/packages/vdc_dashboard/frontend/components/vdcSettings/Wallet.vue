<template>
  <div>
    <div class="actions mb-3">
      <h1 class="d-inline" color="primary" text>Wallet Information</h1>
      <v-btn
        v-if="vdc.wallet"
        class="float-right p-4"
        color="primary"
        text
        target="_blank"
        :href="`https://stellar.expert/explorer/public/account/${vdc.wallet.address}`"
      >
        <v-icon left>mdi-bank</v-icon>List transactions
      </v-btn>
    </div>
    <v-simple-table v-if="vdc.wallet">
      <template v-slot:default>
        <tbody>
          <tr>
            <td>Network</td>
            <td>{{ vdc.wallet.network }}</td>
          </tr>
          <tr>
            <td>Address</td>
            <td>{{ vdc.wallet.address }}</td>
          </tr>
          <tr>
            <td>Secret</td>
            <td>
              <v-text-field
                hide-details
                :value="vdc.wallet.secret"
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
                  vdc.expirationdays < 2
                    ? 'error'
                    : vdc.expirationdays < 14
                    ? 'warning'
                    : 'primary'
                "
                v-for="(balance, i) in vdc.wallet.balances"
                :key="i"
              >
                {{ balance.balance }} {{ balance.asset_code }}
              </v-chip>
            </td>
          </tr>
          <tr>
            <td>VDC expiration date</td>
            <td class="ml-2">
              {{ new Date(vdc.expirationdate * 1000).toLocaleString("en-GB") }}
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
      v-bind="attrs"
      type="date-picker"
    ></v-skeleton-loader>
  </div>
</template>

<script>
module.exports = {
  props: {
    vdc: Object,
  },
  mixins: [dialog],
  data() {
    return {
      showSecret: false,
      qrcode: "",
      attrs: {
        class: "mb-6",
        boilerplate: true,
        elevation: 2,
      },
    };
  },
  methods: {
    getQRCode() {
      this.$api.wallets
        .walletQRCodeImage(this.vdc.wallet.address, this.vdc.price, 3)
        .then((result) => {
          this.qrcode = result.data.data;
        })
        .catch((err) => {
          console.log(err);
        });
    },
  },
  mounted() {
    if (this.vdc.wallet) {
      this.getQRCode();
    }
  },
};
</script>
<style scoped>
h1 {
  color: #1b4f72;
}
</style>
