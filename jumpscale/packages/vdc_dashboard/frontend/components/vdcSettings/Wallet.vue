<template>
  <div>
    <div class="actions mb-3">
      <h1 class="d-inline" color="primary" text>Wallet Information</h1>
      <v-btn
        class="float-right p-4"
        color="primary"
        text
        target="_blank"
        :href="`https://stellar.expert/explorer/public/account/${wallet.address}`"
      >
        <v-icon left>mdi-bank</v-icon>List transactions
      </v-btn>
    </div>
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
                :color="
                  expirationdays < 2
                    ? 'error'
                    : expirationdays < 14
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
              {{ new Date(expirationdate * 1000).toLocaleString("en-GB") }}
            </td>
          </tr>
          <tr>
            <td>QRCode</td>
            <td class="pt-1">
            <div class="text-left ma-1" >
              <v-tooltip top>
                <template v-slot:activator="{ on, attrs }">
                    <img v-bind="attrs" v-on="on" style="border:1px dashed #85929E" :src="`data:image/png;base64, ${qrcode}`"/>
                </template>
                <span>Scan the QRCode to topup wallet using Threefold Connect application</span>
              </v-tooltip>
            </div>
            </td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </div>
</template>

<script>
module.exports = {
  props: { wallet: Object, expirationdays: Number, expirationdate: Number },
  mixins: [dialog],
  data() {
    return {
      showSecret: false,
      qrcode: "",
    };
  },
  methods: {
    getQRCode() {
      this.$api.wallets
        .walletQRCodeImage(this.wallet.address,100,3)
        .then(result => {
          this.qrcode = JSON.parse(result.data).data;
        })
        .catch((err) => {
          console.log(err);
        })
      },
    },
    mounted(){
      if(this.wallet){
        this.getQRCode();
    }
  }
};
</script>
<style scoped>
h1 {
  color: #1b4f72;
}
</style>
