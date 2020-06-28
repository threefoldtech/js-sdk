import time

# TODO: TESTING ONLY
from jumpscale.clients.stellar.stellar import _NETWORK_KNOWN_TRUSTS
from jumpscale.core.base import StoredFactory
from jumpscale.god import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.chatflows.models.user_model import User


class Poll(GedisChatBot):
    """Polls chatflow base
    just inherit from this class and override poll_name and QUESTIONS in your chatflow

    Args:
        GedisChatBot (Parent): contains the chatflows sals main functions

    Raises:
        j.core.exceptions.Runtime: if wrong inheritance happens
        StopChatFlow: if payment is failed
    """

    poll_name = None  # Required
    QUESTIONS = None

    all_users = StoredFactory(User)
    steps = [
        "welcome",
        "payment",
        "vote",
        "result",
    ]

    @chatflow_step()
    def welcome(self):
        user_info = self.user_info()
        j.sals.reservation_chatflow.validate_user(user_info)

        username = user_info["username"].split(".")[0]
        welcome_message = (
            f"# Welcome `{username}` to {self.poll_name} Poll\n<br/>Please note that votes are completely anonymous"
        )
        self.user = self.all_users.get(name=f"{self.poll_name}_{username}")
        self.user.poll_name = self.poll_name
        if self.user.has_voted:
            welcome_message += "\n<br/><br/>`Note: You have already voted.`"

        self.md_show(welcome_message, md=True)

    @chatflow_step(title="Payment")
    def payment(self):
        self.wallet = j.clients.stellar.hamada  # TODO: RESTORE TO STD WALLET

        if not self.user.user_code:
            self.user.user_code = j.data.idgenerator.chars(10)

        if self.user.has_voted and self.user.transaction_hash:
            self.md_show("You have already paid before, Press Next to modify your vote")
        elif self.user.transaction_hash:
            self.md_show("You have already paid before, Press Next to submit your vote")
        else:
            currency = self.single_choice(
                "This will deduce 0.1 unit How would you like to pay in?", ["TFT", "TFTA"], required=True
            )
            qr_code_content = j.sals.zos._escrow_to_qrcode(
                escrow_address=self.wallet.address, escrow_asset=currency, total_amount=0.1, message=self.user.user_code
            )

            message_text = f"""
            <h3> Please make your payment </h3>
            Scan the QR code with your application (do not change the message) or enter the information below manually and proceed with the payment.
            Make sure to add the message (user code) as memo_text
            Please make the transaction and press Next
            <h4> Wallet address: </h4>  {self.wallet.address} \n
            <h4> Currency: </h4>  {currency} \n
            <h4> Amount: </h4>  0.1 \n
            <h4> Message (User code): </h4>  {self.user.user_code} \n
            """
            self.qrcode_show(data=qr_code_content, msg=message_text, scale=4, update=True, html=True)
            # simulate transaction, TODO: REMOVE
            issuer = _NETWORK_KNOWN_TRUSTS["TEST"]["TFT"]
            j.clients.stellar.waleed.transfer(
                self.wallet.address, amount=0.1, asset=f"{currency}:{issuer}", memo_text=self.user.user_code
            )
            time.sleep(2)
            if self._check_payment():
                self.md_show("Payment was successful. Press Next to go to the poll form", md=True)
            else:
                raise StopChatFlow(f"Payment was unsuccessful. Please make sure you entered the correct data")

    def _check_payment(self):
        """Returns True if user has paied alaready, False if not
        """
        transactions = self.wallet.list_transactions()
        for transaction in transactions:
            if transaction.memo_text == self.user.user_code:
                self.user.transaction_hash = transaction.hash
                self.user.save()
                return True

        if self.user.transaction_hash:
            return True

        return False

    @chatflow_step(title="Please fill in the following form", disable_previous=True)
    def vote(self):
        form_answers = {}
        form = self.new_form()
        question, choices = "", ""
        for question, choices in self.QUESTIONS.items():
            form_answers[question] = form.single_choice(question, choices, required=True)
        form.ask()
        form_answers = self._map_vote_results(form_answers)
        self.user.vote_data = form_answers
        self.user.has_voted = True
        self.user.save()

    def _map_vote_results(self, form_answers):
        """takes form answers and returns a sparse array of what user chose
        to be easy in calcualting votes

        example: ["Blue", "Red", "Green", "Orange"]
        if user chose "Red" will [0, 1, 0, 0]

        Args:
            form_answers (dict): form result dictionary
        """

        for question, answer in form_answers.items():
            all_answers_init = len(self.QUESTIONS[question]) * [0]
            answer_index = self.QUESTIONS[question].index(answer.value)
            all_answers_init[answer_index] = 1
            form_answers[question] = all_answers_init
        return form_answers

    @chatflow_step(title="Vote Results")
    def result(self):
        all_users = self.all_users.list_all()

        total_answers = {}
        for username in all_users:
            user = self.all_users.get(username)
            if user.poll_name == self.poll_name:
                user_votes = self.all_users.get(username).vote_data
                for question, answer in user_votes.items():
                    if total_answers.get(question):
                        total_answers[question] = list(map(sum, zip(total_answers[question], answer)))
                    else:
                        total_answers[question] = answer

        total_answers = {k: self._calculate_percent(v) for k, v in total_answers.items()}
        result_msg = ""
        for question, answers in total_answers.items():
            result_msg += f"### {question}\n"
            for i in range(len(answers)):
                answer_name = self.QUESTIONS[question][i]
                result_msg += f"- {answer_name}: {answers[i]}%\n"
            result_msg += "\n"

        print(result_msg)
        self.md_show(result_msg, md=True)

    def _calculate_percent(self, answers_list):
        """Takes the answers list which is a sparse array and map it
        to percentages

        Args:
            answers_list (list)

        Returns:
            list: answers_list mapped to percentages
        """
        total_votes = float(sum(answers_list))
        for i in range(len(answers_list)):
            res = (answers_list[i] / total_votes) * 100
            answers_list[i] = round(res, 2)
        return answers_list
