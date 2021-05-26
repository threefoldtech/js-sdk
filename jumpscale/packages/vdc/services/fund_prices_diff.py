import gevent
from jumpscale.loader import j

from jumpscale.clients.stellar import TRANSACTION_FEES
from jumpscale.sals.vdc import VDCFACTORY
from jumpscale.tools.servicemanager.servicemanager import BackgroundService


class FundPricesDifference(BackgroundService):
    def __init__(self, interval=60 * 60, *args, **kwargs):
        """Service to cover the differences between real price and user price
        """
        super().__init__(interval, *args, **kwargs)

    def job(self):
        j.logger.info(f"FUND PRICES DIFF: Fund prices difference service")
        initialization_wallet_name = j.core.config.get("VDC_INITIALIZATION_WALLET")
        if not initialization_wallet_name:
            j.logger.critical(f"FUND PRICES DIFF: No initialization wallet configured on the VDC deployer")
            return
        initialization_wallet = j.clients.stellar.get(initialization_wallet_name)
        tft = initialization_wallet._get_asset("TFT")
        for vdc_name in VDCFACTORY.list_all():
            vdc_instance = VDCFACTORY.find(vdc_name)
            vdc_instance.load_info()
            vdc_spec_price = vdc_instance.calculate_spec_price(load_info=False) / (24 * 30)  # user price
            # check if vdc in grace period
            if vdc_instance.is_blocked or vdc_instance.is_empty(load_info=False):
                j.logger.info(f"FUND PRICES DIFF: VDC {vdc_instance.instance_name} is empty or in grace period")
                continue
            # check if prepaid has enough money
            prepaid_balance = vdc_instance._get_wallet_balance(vdc_instance.prepaid_wallet)
            if prepaid_balance < vdc_spec_price + TRANSACTION_FEES:
                j.logger.info(
                    f"FUND PRICES DIFF: VDC {vdc_instance.instance_name} hove not enough money for renew plan"
                )
                continue
            elif prepaid_balance > vdc_spec_price:
                # transfer TRANSACTION FEES to the prepaid wallet
                j.logger.info(
                    f"FUND PRICES DIFF: VDC {vdc_instance.instance_name} prepaid wallet has the hour cost but don't have the transaction fees {TRANSACTION_FEES} TFT"
                )
                try:
                    initialization_wallet.transfer(
                        vdc_instance.prepaid_wallet.address, TRANSACTION_FEES, asset=f"{tft.code}:{tft.issuer}"
                    )
                except Exception as e:
                    j.logger.critical(
                        f"FUND PRICES DIFF: Couldn't transfer {TRANSACTION_FEES} to VDC {vdc_name} due to error: {str(e)}"
                    )
                j.logger.info(
                    f"FUND PRICES DIFF: VDC {vdc_instance.instance_name}, funded the transaction fees {TRANSACTION_FEES} TFT to the prepaid wallet"
                )
            vdc_real_price = vdc_instance.calculate_active_units_price() * 60 * 60  # explorer price
            # calculate difference
            diff = vdc_real_price - vdc_spec_price + TRANSACTION_FEES
            if diff > 0:
                # transfer the diff to provisioning wallet
                try:
                    initialization_wallet.transfer(
                        vdc_instance.provision_wallet.address, round(diff, 6), asset=f"{tft.code}:{tft.issuer}"
                    )
                except Exception as e:
                    j.logger.critical(
                        f"FUND PRICES DIFF: Couldn't transfer {diff} to VDC {vdc_name} due to error: {str(e)}"
                    )
                j.logger.info(f"FUND PRICES DIFF: VDC {vdc_instance.instance_name} funded with {diff} TFT")
            gevent.sleep(0.1)


service = FundPricesDifference()
