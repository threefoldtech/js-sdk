from jumpscale.core.base import Base, fields, StoredFactory
import datetime
from jumpscale.loader import j
from jumpscale.clients.stellar import TRANSACTION_FEES
from decimal import Decimal
import datetime


class PaymentTransactionRefund(Base):
    refund_transaction_hash = fields.String()
    success = fields.Boolean(default=False)


class PaymentTransaction(Base):
    transaction_hash = fields.String(required=True)
    transaction_refund = fields.Object(PaymentTransactionRefund)
    success = fields.Boolean(default=False)

    def refund(self, wallet):
        if self.transaction_refund.success:
            return True
        try:
            amount = round(self.get_amount(wallet) - Decimal(TRANSACTION_FEES), 6)
            if amount < 0:
                self.transaction_refund.success = True
            else:
                a = wallet._get_asset()
                sender_address = wallet.get_sender_wallet_address(self.transaction_hash)
                j.logger.info(
                    f"refunding transaction: {self.transaction_hash} with amount: {amount} to address: {sender_address}"
                )
                self.transaction_refund.transaction_hash = wallet.transfer(
                    sender_address, amount=amount, asset=f"{a.code}:{a.issuer}"
                )
                self.transaction_refund.success = True
                j.logger.info(
                    f"transaction: {self.transaction_hash} refunded successfully with amount: {amount} to address: {sender_address} in transaction: {self.transaction_refund.transaction_hash}"
                )
        except Exception as e:
            j.logger.critical(f"failed to refund transaction: {self.transaction_hash} due to error: {str(e)}")
        return self.transaction_refund.success

    def get_amount(self, wallet):
        try:
            effects = wallet.get_transaction_effects(self.transaction_hash)
        except Exception as e:
            j.logger.warning(f"failed to get transaction effects of hash {self.transaction_hash} due to error {str(e)}")
            raise e
        trans_amount = 0
        for effect in effects:
            if effect.asset_code != "TFT":
                continue
            trans_amount += effect.amount
        return trans_amount


class PaymentResult(Base):
    success = fields.Boolean(default=False)
    extra_paid = fields.Boolean(default=False)
    transactions = fields.List(fields.Object(PaymentTransaction))

    def refund_extra(self):
        if self.extra_paid and self.parent.refund_extra:
            for transaction in self.transactions:
                if transaction.success:
                    trans_amount = transaction.get_amount(self.parent.wallet)
                    diff = float(trans_amount) - self.parent.amount
                    if diff <= TRANSACTION_FEES:
                        self.extra_paid = False
                        break
                    sender_address = self.parent.wallet.get_sender_wallet_address(transaction.transaction_hash)
                    amount = round(diff - TRANSACTION_FEES, 6)
                    try:
                        j.logger.info(
                            f"refunding extra amount: {amount} of transaction {transaction.transaction_hash} to address: {sender_address}"
                        )
                        a = self.parent.wallet._get_asset()
                        refund_hash = self.parent.wallet.transfer(
                            sender_address, amount=amount, asset=f"{a.code}:{a.issuer}"
                        )
                        self.extra_paid = False
                        j.logger.info(
                            f"extra amount: {amount} of transaction {transaction.transaction_hash} refunded successfully in transaction: {refund_hash} to address: {sender_address}"
                        )
                    except Exception as e:
                        j.logger.critical(
                            f"failed to refund extra amount {amount} for payment: {self.parent.payment_id} due to error: {str(e)}"
                        )
            self.parent.save()
        return self.extra_paid


class Payment(Base):
    payment_id = fields.String()
    wallet_name = fields.String(required=True)
    amount = fields.Float(required=True)
    memo_text = fields.String(default=lambda: j.data.idgenerator.chars(28))
    created_at = fields.DateTime(default=datetime.datetime.utcnow)
    deadline = fields.DateTime(default=lambda: datetime.datetime.utcnow() + datetime.timedelta(minutes=5))
    result = fields.Object(PaymentResult, required=True)
    refund_extra = fields.Boolean(default=True)
    description = fields.String()

    def is_finished(self):
        if self.deadline.timestamp() < j.data.time.utcnow().timestamp or self.result.success:
            return True

        return False

    @property
    def wallet(self):
        return j.clients.stellar.get(self.wallet_name)

    def update_status(self):
        if self.is_finished():
            return
        if self.amount == 0:
            self.result.success = True
            self.save()
            return
        j.logger.info(f"updating payment: {self.payment_id} status")
        transactions = self.wallet.list_transactions()
        current_transactions = {t.transaction_hash: t for t in self.result.transactions}
        for transaction in transactions:
            transaction_hash = transaction.hash
            if transaction_hash in current_transactions:
                continue
            trans_memo_text = transaction.memo_text
            if not trans_memo_text:
                continue

            if trans_memo_text != self.memo_text:
                continue

            j.logger.info(f"adding transaction {transaction_hash} to payment: {self.payment_id}")

            trans_obj = PaymentTransaction()
            trans_obj.transaction_hash = transaction_hash
            self.result.transactions.append(trans_obj)

            if not self.result.success:
                try:
                    trans_amount = trans_obj.get_amount(self.wallet)
                    j.logger.info(
                        f"adding transaction {transaction_hash} to payment: {self.payment_id} with amount: {trans_amount}"
                    )
                except Exception as e:
                    j.logger.error(
                        f"failed to update payment {self.instance_name} with transaction {transaction_hash} due to error {str(e)}"
                    )
                    continue
                if trans_amount >= Decimal(self.amount) or abs(trans_amount - Decimal(self.amount)) <= 0.000001:
                    j.logger.info(
                        f"payment: {self.payment_id} fulfilled by transaction: {transaction_hash} with amount: {trans_amount}"
                    )
                    trans_obj.success = True
                    self.result.success = True
                    if trans_amount > Decimal(self.amount):
                        j.logger.info(f"payment: {self.payment_id} is marked as extra paid")
                        self.result.extra_paid = True
            self.save()


class PaymentFactory(StoredFactory):
    def find_by_id(self, payment_id):
        instance_name = f"payment_{payment_id}"
        return self.find(instance_name)

    def list_failed_payments(self):
        for name in self.list_all():
            payment = self.find(name)
            payment.update_status()
            if payment.is_finished():
                if not payment.result.success:
                    yield payment
                else:
                    for transaction in payment.result.transactions:
                        if not transaction.success and not transaction.transaction_refund.success:
                            yield payment
                            break

    def list_active_payments(self):
        for name in self.list_all():
            payment = self.find(name)
            if not payment.is_finished():
                yield payment

    def list_extra_paid_payments(self):
        _, _, payments = self.find_many(refund_extra=True)
        for payment in payments:
            if payment.result.extra_paid and payment.is_finished():
                yield payment


PAYMENT_FACTORY = PaymentFactory(Payment)
PAYMENT_FACTORY.always_reload = True


class RefundRequest(Base):
    payment_id = fields.String(required=True)
    success = fields.Boolean(default=False)
    refund_transaction_hash = fields.String()
    last_tried = fields.DateTime()
    amount = fields.Float(default=-1)

    def apply(self):
        payment = PAYMENT_FACTORY.find_by_id(self.payment_id)
        if not payment.is_finished():
            j.logger.warning(f"can't refund active payment {self.payment_id}")
            return False

        self.last_tried = datetime.datetime.utcnow()
        amount = payment.amount
        # check if refund extra is False. then amount should be same as successful transaction in case of extra was paid but not refunded automatically
        sender_address = None
        for transaction in payment.result.transactions:
            if transaction.success:
                sender_address = payment.wallet.get_sender_wallet_address(transaction.transaction_hash)
                if not payment.refund_extra:
                    amount = float(transaction.get_amount(payment.wallet))

        # if a specific amount was specified by the refund request
        if self.amount > 0:
            amount = self.amount

        if amount <= TRANSACTION_FEES or not sender_address:
            self.success = True
        else:
            try:
                a = payment.wallet._get_asset()
                self.refund_transaction_hash = payment.wallet.transfer(
                    sender_address, amount=round(amount - TRANSACTION_FEES, 6), asset=f"{a.code}:{a.issuer}"
                )
                self.success = True
                j.logger.info(
                    f"refund request successful for payment: {self.payment_id} amount: {amount} to address: {sender_address} in transaction: {self.refund_transaction_hash}"
                )
            except Exception as e:
                j.logger.critical(f"failed to apply refund request for payment {self.payment_id} due to error {str(e)}")
        self.save()
        return self.success


class RefundFactory(StoredFactory):
    def list_active_requests(self):
        _, _, refunds = self.find_many(success=False)
        return refunds


REFUND_FACTORY = RefundFactory(RefundRequest)
REFUND_FACTORY.always_reload = True
