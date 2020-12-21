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
  props: { wallet: Object },
  mixins: [dialog],
  data() {
    return {
      showSecret: false,
    };
  },
};
</script>
