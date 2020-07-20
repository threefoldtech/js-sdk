<template>
  <base-dialog title="Wallet details" v-model="dialog" :loading="loading">
    <template #default>
      <v-simple-table v-if="wallet">
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
          </tbody>
        </template>
      </v-simple-table>
    </template>
    <template #actions>
      <v-btn text @click="updateTrustlines">Update trustlines</v-btn>
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
      showSecret: false
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
      this.$api.wallets.get(this.name).then((response) => {
        this.wallet = JSON.parse(response.data).data
      }).finally(() => {
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
