from .models import PAYMENT_FACTORY, REFUND_FACTORY
import uuid, datetime
import gevent
from jumpscale.loader import j


class BillingManager:
    def submit_payment(self, amount, wallet_name, refund_extra=True, expiry=5, description=""):
        payment_id = uuid.uuid4().hex
        instance_name = f"payment_{payment_id}"
        payment = PAYMENT_FACTORY.new(
            instance_name,
            payment_id=payment_id,
            amount=round(amount, 6),
            wallet_name=wallet_name,
            refund_extra=refund_extra,
            description=description,
        )
        payment.deadline = datetime.datetime.utcnow() + datetime.timedelta(minutes=expiry)
        payment.save()
        j.logger.info(
            f"payment {payment_id} submitted for wallet: {wallet_name} amount: {amount}, description: {description}, expiry: {expiry}, memo_text: {payment.memo_text}"
        )
        return payment_id, payment.memo_text

    def wait_payment(self, payment_id, bot=None, notes=None):
        j.logger.info(f"waiting payment: {payment_id}")
        payment = PAYMENT_FACTORY.find_by_id(payment_id)
        if bot:
            self._show_payment(bot, payment, notes)

        while not payment.is_finished():
            gevent.sleep(3)
            payment = PAYMENT_FACTORY.find_by_id(payment_id)
        j.logger.info(f"payment: {payment_id} result {payment.result.success}")
        return payment.result.success

    def _show_payment(self, bot, payment_obj, notes=None):
        notes = notes or []
        qr_code = (
            f"TFT:{payment_obj.wallet.address}?amount={payment_obj.amount}&message={payment_obj.memo_text}&sender=me"
        )
        notes_text = "\n".join([f"<h4>Note: {note}</h4>" for note in notes])
        qr_encoded = j.tools.qrcode.base64_get(qr_code, scale=2)
        msg_text = f"""Please scan the QR Code below for the payment details
        <div class="text-center">
            <img style="border:1px dashed #85929E" src="data:image/png;base64,{qr_encoded}"/>
        </div>
        <h4> Destination Wallet Address: </h4>  {payment_obj.wallet.address} \n
        <h4> Currency: </h4>  TFT \n
        <h4> Memo Text: </h4>  {payment_obj.memo_text} \n
        <h4> Total Amount: </h4> {payment_obj.amount} TFT \n
        {notes_text}
        <h5>Inserting the memo-text is an important way to identify a transaction recipient beyond a wallet address. Failure to do so will result in a failed payment. Please also keep in mind that an additional Transaction fee of 0.1 TFT will automatically occur per transaction.</h5>
        """
        bot.md_show_update(msg_text, html=True)

    def refund_failed_payments(self):
        for payment in PAYMENT_FACTORY.list_failed_payments():
            refund_result = True
            for transaction in payment.result.transactions:
                if transaction.success or transaction.transaction_refund.success:
                    continue
                j.logger.info(f"refunding transaction: {transaction.transaction_hash} of payment: {payment.payment_id}")
                refund_result = refund_result and transaction.refund(payment.wallet)
                payment.save()

    def issue_refund(self, payment_id, amount=-1):
        instance_name = f"refund_{payment_id}"
        request = REFUND_FACTORY.new(instance_name, payment_id=payment_id, amount=amount)
        request.save()
        j.logger.info(f"refund request created for payment: {payment_id}")
        return

    def check_refund(self, payment_id):
        instance_name = f"refund_{payment_id}"
        request = REFUND_FACTORY.find(instance_name)
        if not request:
            raise j.exceptions.Input(f"not refunds were issues for payment {payment_id}")
        return request.success

    def process_refunds(self):
        for request in REFUND_FACTORY.list_active_requests():
            j.logger.info(f"applying active refund for payment: {request.payment_id}")
            request.apply()

    def process_payments(self):
        for payment in PAYMENT_FACTORY.list_active_payments():
            j.logger.info(f"updating active payment: {payment.payment_id}")
            payment.update_status()

    def refund_extra(self):
        for payment in PAYMENT_FACTORY.list_extra_paid_payments():
            j.logger.info(f"refund extra paid for payment: {payment.payment_id}")
            payment.result.refund_extra()
