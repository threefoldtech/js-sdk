import os

from jumpscale.loader import j


def get_excluded_wallets():
    """Get used wallet in the CI.

    Returns:
        list: excluded wallets addresses.
    """
    excluded_wallets = []
    wallets_secrets_env = ["WALLET_SECRET", "SOURCE_WALLET_SECRET", "DESTINATION_WALLET_SECRET"]
    for env in wallets_secrets_env:
        wallet_secret = os.environ.get(env)
        if wallet_secret:
            wallet = j.clients.stellar.get("test")
            wallet.secret = wallet_secret
            excluded_wallets.append(wallet.address)
    return excluded_wallets


def get_activation_wallet_address():
    """Get activation wallets address.

    Returns:
        str: activation wallet address.
    """
    activation_address = "GBSGNS22IGOPBV2NGS2OL76SMARQ6S7YRHRRASQUTBMZHMRYFYQW7F5Z"
    wallet = j.clients.stellar.find("activation_wallet")
    if wallet:
        activation_address = wallet.address
    return activation_address


def get_telegram_client():
    """Create telegram client for sending wallets' secret that will fail to merge.

    Returns:
        set: telegram client, channel id.
    """
    from telegram import Bot

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    cl = None
    if bot_token and chat_id:
        cl = Bot(bot_token)
    return cl, chat_id


def merge_wallets(merge_address, telegram_cl=None, chat_id="", exclude=[]):
    """Merge all wallets except the excluded ones.

    Args:
        merge_address (str): merge wallet address.
        telegram_cl (object, optional): telegram client. Defaults to None.
        chat_id (str): telegram channel id.
        exclude (list, optional): wallets' addresses to be excluded. Defaults to [].
    """
    nmerged = 0
    for w_name in j.clients.stellar.list_all():
        wallet = j.clients.stellar.get(w_name)
        if wallet.address in exclude:
            continue
        try:
            wallet.merge_into_account(merge_address)
            nmerged += 1
        except Exception as e:
            j.logger.critical(f"Failed to merge wallet {wallet.instance_name} due to error: {str(e)}")
            if telegram_cl and chat_id:
                telegram_cl.send_message(chat_id=chat_id, text=f"Failed to merge wallet: {wallet.secret}")

    j.logger.info(f"number of the merged wallets: {nmerged}")


if __name__ == "__main__":
    excluded_wallets = get_excluded_wallets()
    activation_address = get_activation_wallet_address()
    telegram_cl, chat_id = get_telegram_client()
    merge_wallets(activation_address, telegram_cl, chat_id, excluded_wallets)
