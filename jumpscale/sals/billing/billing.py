from .models import PAYMENT_FACTORY, REFUND_FACTORY
import uuid, datetime
import gevent
from jumpscale.loader import j
from jumpscale.clients.stellar import TRANSACTION_FEES


class BillingManager:
    def submit_payment(self, amount, wallet_name, refund_extra=True, expiry=5, description=""):
        """Submit payment.

        Args:
            amount (float): amount of current payment.
            wallet_name (str): name of wallet that submit the payment.
            refund_extra (bool, optional): if the payment has extra amount it will be refunded. Defaults to True.
            expiry (int, optional): time in minutes the payment will expire after it. Defaults to 5.
            description (str, optional): describe the payment. Defaults to "".

        Returns:
            tuple(str, str): payment_id and memo_text that used as confirmation for the payment.
        """
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
        """Wait payment amount of time.

        Args:
            payment_id (str): payment id to wait on.
            bot : used in case of using it with threebot deployer or VDC chatflow. Defaults to None.
            notes (str, optional): optional note that appears while waiting. Defaults to None.

        Returns:
            bool: return result of this payment, True if payment finished, False if payment expired.
        """
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
        msg_text = f"""Please scan the QR Code below (Using ThreeFold Connect Application) for the payment details
        <div class="text-center">
            <img style="border:1px dashed #85929E" src="data:image/png;base64,{qr_encoded}"/>
        </div>
        <h4> Destination Wallet Address: </h4>  {payment_obj.wallet.address} \n
        <h4> Currency: </h4>  TFT \n
        <h4> Memo Text (Message): </h4>  {payment_obj.memo_text} \n
        <h4> Total Amount: </h4>  {payment_obj.amount} TFT \n
        {notes_text}
        <h5>When using manual payment please note that inserting the memo-text is an important way to identify a transaction recipient beyond a wallet address. Failure to do so will result in a failed payment. Please also keep in mind that an additional Transaction fee of {TRANSACTION_FEES} TFT will automatically occur per transaction.</h5>
        """
        bot.md_show_update(msg_text, html=True)

    def refund_failed_payments(self):
        """Refund any failed payment.
        Example: transfer amount less than payment amount.
        """
        for payment in PAYMENT_FACTORY.list_failed_payments():
            refund_result = True
            for transaction in payment.result.transactions:
                if transaction.success or transaction.transaction_refund.success:
                    continue
                j.logger.info(f"refunding transaction: {transaction.transaction_hash} of payment: {payment.payment_id}")
                refund_result = refund_result and transaction.refund(payment.wallet)
                payment.save()

    def issue_refund(self, payment_id, amount=-1):
        """Issue Refund.
        It is used if refund needed even after successfull payment.
        Args:
            payment_id (str): payment id of the payment needs to be refunded.
            amount (int, optional): amount of the refund value. Defaults to -1(Meaning refund the total amount of the payment).
        """
        instance_name = f"refund_{payment_id}"
        request = REFUND_FACTORY.new(instance_name, payment_id=payment_id, amount=amount)
        request.save()
        j.logger.info(f"refund request created for payment: {payment_id}")
        return

    def check_refund(self, payment_id):
        """Check refund request status.

        Args:
            payment_id (str): payment id of the payment needs to check refund status.

        Raises:
            j.exceptions.Input: raise error if no refund request belong to the payment.

        Returns:
            bool: return the state of the refund request, True if refund success.
        """
        instance_name = f"refund_{payment_id}"
        request = REFUND_FACTORY.find(instance_name)
        if not request:
            raise j.exceptions.Input(f"not refunds were issues for payment {payment_id}")
        return request.success

    def process_refunds(self):
        """Process any active refund.
        list all active refund and apply it.
        """
        for request in REFUND_FACTORY.list_active_requests():
            j.logger.info(f"applying active refund for payment: {request.payment_id}")
            request.apply()

    def process_payments(self):
        """Process any active payment.
        list all active payment and apply it.
        """
        for payment in PAYMENT_FACTORY.list_active_payments():
            j.logger.info(f"updating active payment: {payment.payment_id}")
            payment.update_status()

    def refund_extra(self):
        """Process any active extra refund.
        list all active extra refund and apply it.
        """
        for payment in PAYMENT_FACTORY.list_extra_paid_payments():
            j.logger.info(f"refund extra paid for payment: {payment.payment_id}")
            payment.result.refund_extra()
