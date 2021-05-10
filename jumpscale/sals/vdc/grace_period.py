from datetime import datetime

from jumpscale.core.base import Base, StoredFactory, fields
from jumpscale.loader import j
from jumpscale.clients.stellar import TRANSACTION_FEES


GP_WALLET_NAME = j.config.get("GRACE_PERIOD_WALLET", "grace_period")


class VDCGracePeriodFactory(StoredFactory):
    def list_active_grace_periods(self):
        for name in self.list_all():
            gp = self.get(name)
            if gp.paid_amount >= gp.fund_amount:
                continue
            yield gp

    def check_grace_period(self, vdc_instance_name) -> bool:
        _, _, result = self.find_many(vdc_instance_name=vdc_instance_name)
        for gp in result:
            if gp.paid_amount < gp.fund_amount:
                return True

        return False

    def is_eligible(self, vdc_instance) -> bool:
        if vdc_instance.is_empty():
            j.logger.debug(f"vdc {vdc_instance.vdc_name} is empty and not eligible")
            return False

        if self.check_grace_period(vdc_instance.instance_name):
            j.logger.debug(f"vdc {vdc_instance.vdc_name} is in grace period and not eligible")
            return False

        if vdc_instance.expiration_date.timestamp() > j.data.time.utcnow().timestamp + j.config.get(
            "GRACE_PERIOD_TRIGGER", 3
        ):
            j.logger.debug(f"vdc {vdc_instance.vdc_name} still has expiration and not eligible")
            return False
        j.logger.debug(f"vdc {vdc_instance.vdc_name} eligible to grace period")
        return True

    def start_grace_period(self, vdc_instance):
        if not self.is_eligible(vdc_instance):
            return

        gp = self.new(
            f"{vdc_instance.instance_name}_{j.data.time.utcnow().timestamp}",
            vdc_instance_name=vdc_instance.instance_name,
        )
        j.logger.debug(f"vdc {vdc_instance.vdc_name} enters grace period")
        return gp.apply()


class GracePeriodModel(Base):
    """
    - check grace period
      - pools exiration is set to lower than 2 days (configurable)
      - prepaid wallet has less than one hour to cover resources

    - apply grace period
      - extend pools for 2 weeks (renew plan)
      - save vdc to be in grace period
      - apply action

    - actions during grace period
      - check hourly for balance (prepaid):
        - deduce tokens until it covers the grace period
        - revert grace period

    - revert of grace period
      - revert action to normal

    """

    vdc_instance_name = fields.String(required=True)
    fund_amount = fields.Float()  # amount we will take from user
    fund_at = fields.DateTime(default=datetime.utcnow)
    paid_amount = fields.Float()
    user_grace_period_id = fields.String(default=lambda: j.data.idgenerator.chars(28))

    def apply(self):
        vdc = j.sals.vdc.find(self.vdc_instance_name, load_info=True)
        deployer = vdc.get_deployer()
        deployer._set_wallet(GP_WALLET_NAME)
        renewal_days = j.config.get("GRACE_PERIOD_DAYS", 14)
        deployer.renew_plan(duration=renewal_days)
        j.logger.info(f"vdc {self.vdc_instance_name} renewed grace period plan")
        self.fund_amount = (vdc.calculate_spec_price() * renewal_days) / 30
        self.save()
        vdc.apply_grace_period_action()
        j.logger.info(f"vdc {self.vdc_instance_name} grace period action has been applied")

    def revert(self):
        vdc = j.sals.vdc.find(self.vdc_instance_name, load_info=True)
        vdc.revert_grace_period_action()
        j.logger.info(f"vdc {self.vdc_instance_name} grace period action has been reverted")

    def update_status(self):
        vdc = j.sals.vdc.find(self.vdc_instance_name)
        try:
            balance = vdc._get_wallet_balance(vdc.prepaid_wallet)
        except Exception as e:
            j.logger.error(f"couldn't get balance prepaid wallet of {self.vdc_instance_name}, error was {e} ")
        else:
            if balance > TRANSACTION_FEES:
                grace_period_wallet = j.clients.stellar.find(GP_WALLET_NAME)
                amount = round(self.fund_amount - self.paid_amount, 6)
                if balance < amount + TRANSACTION_FEES:
                    amount = balance - TRANSACTION_FEES
                j.logger.info(
                    f"vdc {self.vdc_instance_name} has enough balance and transfering {amount} to grace period wallet"
                )
                vdc.pay_amount(
                    grace_period_wallet.address, amount, vdc.prepaid_wallet, memo_text=self.user_grace_period_id
                )
                self.paid_amount += amount
                self.save()

            if self.paid_amount >= self.fund_amount:
                j.logger.info(f"vdc {self.vdc_instance_name} has paid, grace period action has been reverted")
                self.revert()


GRACE_PERIOD_FACTORY = VDCGracePeriodFactory(GracePeriodModel)
GRACE_PERIOD_FACTORY.always_reload = True
