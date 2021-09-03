from decimal import Decimal
import time

from jumpscale.loader import j

from jumpscale.packages.admin.services.notifier import MAIL_QUEUE


def get_payment_amount(pool):
    escrow_info = pool.escrow_information
    resv_id = pool.reservation_id
    escrow_address = escrow_info.address
    escrow_asset = escrow_info.asset
    total_amount = escrow_info.amount
    if not total_amount:
        return
    total_amount_dec = Decimal(total_amount) / Decimal(1e7)
    total_amount = "{0:f}".format(total_amount_dec)
    return resv_id, escrow_address, escrow_asset, total_amount


def pay_pool(pool_info):
    # Get the amount of payment
    res = get_payment_amount(pool_info)
    if not res:
        j.logger.error(f"Faild to get payment info for {pool_info}")
        return False
    resv_id, escrow_address, escrow_asset, total_amount = res
    # Get the user wallets
    wallets = j.sals.reservation_chatflow.reservation_chatflow.list_wallets()
    for wallet_name, wallet_val in wallets.items():
        j.logger.info(f"Trying to pay reservation: {resv_id} with wallet {wallet_name}")
        try:
            wallet_val.transfer(
                destination_address=escrow_address, amount=total_amount, asset=escrow_asset, memo_text=f"p-{resv_id}"
            )
            return True
        except:
            j.logger.warning(f"failed to reservation: {resv_id} with wallet {wallet_name}")
    return False


def check_pool_expiration(pool, threshold_days=14):
    remaining_days = (pool.empty_at - time.time()) / 86400  # converting seconds to days
    return remaining_days < threshold_days and remaining_days > 0


def calculate_pool_units(pool, days=14):
    cu = pool.active_cu * 60 * 60 * 24 * days
    su = pool.active_su * 60 * 60 * 24 * days
    return cu, su


def auto_extend_pools():
    pools = j.sals.zos.get().pools.list()
    for pool in pools:
        if check_pool_expiration(pool):
            cu, su = calculate_pool_units(pool)
            auto_extend_pool(pool.pool_id, int(cu), int(su))


def auto_extend_pool(pool_id, cu, su, currencies=None):
    currencies = currencies or ["TFT"]
    pool_info = None
    try:
        pool_info = j.sals.zos.get().pools.extend(pool_id, cu, su, 0, currencies=currencies)
    except Exception as e:
        send_pool_info_mail(pool_id)
        j.logger.error(f"Error happend during extending the pool, {str(e)}")
    if not pay_pool(pool_info):
        send_pool_info_mail(pool_id)


def send_pool_info_mail(pool_id, sender="support@threefold.com"):
    recipients_emails = []
    user_mail = j.core.identity.me.email
    recipients_emails.append(user_mail)
    escalation_emails = j.core.config.get("ESCALATION_EMAILS", [])
    recipients_emails.extend(escalation_emails)
    message = (
        f"The pool with Id {pool_id} is about to expire and we are not "
        "able to extend it automatically, "
        "please check the fund in your wallets and extend it manually "
        "or contact our support team"
    )
    mail_info = {
        "recipients_emails": recipients_emails,
        "sender": sender,
        "subject": "Auto Extend Pools",
        "message": message,
    }
    j.core.db.rpush(MAIL_QUEUE, j.data.serializers.json.dumps(mail_info))
