import { Service } from "../common/api";

const BASE_URL = "/admin/actors/wallet";

class WalletService extends Service {
    constructor() {
        super(BASE_URL);
    }

    createWallet(name) {
        return this.postCall("create_wallet", {
            name: name
        });
    }

    getWalletInfo(name) {
        return this.postCall("get_wallet_info", {
            name: name
        });
    }

    getWallets() {
        return this.getCall("get_wallets");
    }

    updateTrustLines(name) {
        return this.postCall("update_trustlines", {
            name: name
        });
    }

    importWallet(name, secret, network) {
        return this.postCall("import_wallet", {
            name: name,
            secret: secret,
            network: network
        });
    }

    deleteWallet(name) {
        return this.postCall("delete_wallet", {
            name: name
        });
    }
}

export const wallet = new WalletService();
