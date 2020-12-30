<template>
  <div>
    <base-component title="Wallets" icon="mdi-wallet" :loading="loading">
      <template #actions>
            <v-btn color="primary" text @click.stop="dialogs.create = true">
              <v-icon left>mdi-plus</v-icon>Create
            </v-btn>

        <v-btn color="primary" text @click.stop="dialogs.import = true">
          <v-icon left>mdi-import</v-icon>Import
        </v-btn>
      </template>

      <template #default>
        <v-row align="start" justify="start">
          <v-card
            class="ma-4 mt-2"
            width="300"
            v-for="wallet in wallets"
            :key="wallet.name"
            @click.stop="open(wallet.name)"
          >
            <v-card-title class="primary--text">{{wallet.name}}</v-card-title>
            <v-card-subtitle>{{wallet.network}}</v-card-subtitle>
            <v-card-text>{{wallet.address}}</v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn icon @click.stop="selected = wallet.name; dialogs.delete = true">
                <v-icon color="primary" left>mdi-delete</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-row>
      </template>
    </base-component>

    <create-wallet v-model="dialogs.create" @done="listWallets"></create-wallet>
    <import-wallet v-model="dialogs.import" @done="listWallets"></import-wallet>
    <delete-wallet v-model="dialogs.delete" @done="listWallets" :name="selected"></delete-wallet>
    <wallet-info v-model="dialogs.wallet" :name="selected"></wallet-info>
  </div>
</template>

<script>
module.exports = {
  components: {
    "create-wallet": httpVueLoader("./Create.vue"),
    "import-wallet": httpVueLoader("./Import.vue"),
    "delete-wallet": httpVueLoader("./Delete.vue"),
    "wallet-info": httpVueLoader("./Wallet.vue"),
  },
  data() {
    return {
      wallets: [],
      selected: null,
      dialogs: {
        create: null,
        funded: null,
        import: null,
        delete: null,
        wallet: null,
      },
      loading: false,
    };
  },
  methods: {
    open(wallet) {
      this.selected = wallet;
      this.dialogs.wallet = true;
    },
    listWallets() {
      this.loading = true;
      this.$api.wallets
        .list()
        .then((response) => {
          this.wallets = JSON.parse(response.data).data;
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
  mounted() {
    this.listWallets();
  },
};
</script>
