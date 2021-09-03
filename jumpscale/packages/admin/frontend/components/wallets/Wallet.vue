<template>
  <base-dialog title="Wallet details" v-model="dialog" :loading="loading">
    <template #default>
      <template v-if="error">
      <v-alert type="error">Failed to load wallet {{ name }}, is it possible the wallet isn't activated?</v-alert>
      </template>

      <v-simple-table v-if="wallet && wallet.network">
        <template v-slot:default>
          <tbody>
            <tr>
              <td>Name</td>
              <td>{{ name }}</td>
            </tr>
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
                  readonly solo flat
                  :append-icon="showSecret ? 'mdi-eye' : 'mdi-eye-off'"
                  :type="showSecret ? 'text' : 'password'"
                  @click:append="showSecret = !showSecret"
                ></v-text-field>
              </td>
            </tr>
            <tr>
              <td>Balances</td>
              <td class="pt-1">
                <v-chip outlined class="ma-2" v-for="(balance, i) in wallet.balances" :key="i">
                  {{balance.asset_code}} {{balance.balance}}
                </v-chip>
              </td>
            </tr>
            <tr>
              <td>QRCode</td>
              <td class="pt-1">
                <v-tooltip top>
                  <template v-slot:activator="{ on, attrs }">
                    <div class="text-left ma-4" v-bind="attrs" v-on="on">
                      <img style="border:1px dashed #85929E" :src="`data:image/png;base64, ${wallet.qrcode}`"/>
                    </div>
                  </template>
                  <span>Scan the QRCode to topup wallet using Threefold Connect application</span>
                </v-tooltip>
              </td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </template>
    <template #actions>
      <template v-if="!hasTft && this.error">
            <v-btn text @click="updateTrustlines">Accept TFT</v-btn>
      </template>
      <v-btn text @click="close">Close</v-btn>
    </template>
  </base-dialog>
</template>

<script>

module.exports = {
  props: {name: String},
  mixins: [dialog],
  data () {
    return {
      wallet: null,
      hasTft: false,
      showSecret: false,
      error: null,
    }
  },
  watch: {
    dialog (val) {
      if (val) {
        this.getWalletInfo()
      } else {
        this.wallet = null
      }
    }
  },
  methods: {
    getWalletInfo () {
      this.loading = true
      this.hasTft = false
      this.$api.wallets.get(this.name).then((response) => {
        this.error = JSON.parse(response.data).error
        if ( this.error ) {
          console.log(this.error)
          return
        }
        this.wallet = JSON.parse(response.data).data
        for (let b of this.wallet.balances) {
          if (b.asset_code.toUpperCase() === "TFT"){
            this.hasTft = true
            break
          }
        }
      }).catch (err => {
        console.log(err)
        this.error = err;
      }
      ).finally(() => {
        this.loading = false
      })
    },
    updateTrustlines(){
      this.loading = true
      this.$api.wallets.updateTrustlines(this.name).then((response) => {
        this.done("Trustlines updated", "success")
      }).finally(() => {
        this.loading = false
      })

    }
  }
}
</script>
