from textwrap import dedent

from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.chatflows.models.voter_model import User

WALLET_NAME = "polls_receive"
MANIFESTO_VERSION = "2.0.1"

all_users = StoredFactory(User)
all_users.always_reload = True


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

    steps = ["initialize", "welcome", "payment", "custom_votes", "result"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.QUESTIONS = {}
        self.extra_data = {}
        self.metadata = {}
        self.custom_answers = {}

        if not j.clients.stellar.find(WALLET_NAME):
            raise j.core.exceptions.Runtime(f"Wallet {WALLET_NAME} is not configured, please create it.")

        self.wallet = j.clients.stellar.get(WALLET_NAME)

    def _get_wallets_as_md(self, wallets):
        result = "\n"
        for item in wallets:
            result += f"- `{item}` has {self._get_voter_balance(item)} (TFT+TFTA)\n"
        return result

    @chatflow_step()
    def initialize(self):
        user_info = self.user_info()

        username = user_info["username"].split(".")[0]
        welcome_message = f"# Welcome `{username}` to {self.poll_name.capitalize()} Poll\n<br/>The detailed poll results are only visible to the tfgrid council members"
        self.user = all_users.get(name=f"{self.poll_name}_{username}")
        self.user.poll_name = self.poll_name
        if self.user.has_voted:
            welcome_message += "\n<br/><br/>`Note: You have already voted.`"

        if self.user.has_voted:
            actions = ["Edit My Vote", "See Results"]
            action = self.single_choice(welcome_message, options=actions, required=True, md=True)
            if action == actions[1]:
                self.result()
                self.end()
        else:
            self.md_show(welcome_message, md=True)

    @chatflow_step()
    def welcome(self):
        pass

    @chatflow_step(title="Loading Wallets")
    def payment(self):
        def _pay(msg=""):
            amount = 0.1
            currency = self.single_choice(
                "We need to know how many tokens you have to allow weighted vote results, "
                "in order to do this we need to know all of your wallets addresses you want us to consider in this poll. "
                "The idea is you send us a small transaction that costs 0.1 tokens. "
                "Then we will be able to calculate the sum of the TFTs and TFTAs you have in all of the wallets you added. Now you can start adding your wallets "
                "Which token would you like to continue the transaction with?",
                ["TFT", "TFTA"],
                required=True,
            )

            qr_code_content = j.sals.zos.get()._escrow_to_qrcode(
                escrow_address=self.wallet.address,
                escrow_asset=currency,
                total_amount=amount,
                message=self.user.user_code,
            )

            message_text = f"""\
            <h3>Make a Payment</h3>
            Scan the QR code with your wallet (do not change the message) or enter the information below manually and proceed with the payment.
            Make sure to add the message (user code) as memo_text
            Please make the transaction and press Next
            <h4> Wallet address: </h4>  {self.wallet.address}
            <h4> Currency: </h4>  {currency}
            <h4> Amount: </h4>  {amount}
            <h4> Message (User code): </h4>  {self.user.user_code}
            """
            self.qrcode_show(data=qr_code_content, msg=dedent(message_text), scale=4, update=True, html=True, md=True)
            if self._check_payment(timeout=360):
                return True
            else:
                return False

        def _pay_again(msg=""):
            while True:
                pay_again = self.single_choice(
                    msg
                    or f"Wallets added: {self._get_wallets_as_md(self.user.wallets_addresses)}\nDo you like to add another wallet?",
                    ["YES", "NO"],
                    md=True,
                )
                if pay_again == "NO":
                    break
                if not _pay():
                    _pay_again(
                        "Error adding the wallet, Please make sure you transaction is completed.\n do you want to try again ?"
                    )

        if not self.user.user_code:
            self.user.user_code = j.data.idgenerator.chars(10)
        # Payment
        if self.user.has_voted and len(self.user.wallets_addresses) > 0:
            self.md_show(
                f"You have already added wallets: {self._get_wallets_as_md(self.user.wallets_addresses)}\n, Press Next to add another wallet and modify your vote",
                md=True,
            )
            _pay_again()

        elif len(self.user.wallets_addresses) > 0:
            self.md_show(
                f"You have already added wallets: {self._get_wallets_as_md(self.user.wallets_addresses)}\n, Press Next to add another wallet and submit your vote",
                md=True,
            )
            _pay_again()
        else:
            if _pay():
                _pay_again()
            else:
                self.stop("Error adding the wallet, Please make sure you transaction is completed.\n Please try again")

    def _check_payment(self, timeout):
        """Returns True if user has paid already, False if not"""
        now = j.data.time.get().timestamp
        remaning_time = j.data.time.get(now + timeout).timestamp
        while remaning_time > now:
            remaning_time_msg = j.data.time.get(remaning_time).humanize(granularity=["minute", "second"])
            payment_message = (
                "# Payment being processed...\n"
                f"Process will be cancelled if payment is not successful {remaning_time_msg}"
            )
            self.md_show_update(payment_message, md=True)
            user_wallets_count = len(self.user.wallets_addresses)
            transactions = self.wallet.list_transactions()
            for transaction in transactions:
                if transaction.memo_text == self.user.user_code:
                    if transaction.hash not in self.user.transaction_hashes:
                        self.user.transaction_hashes.append(transaction.hash)
                    user_wallet = self.wallet.get_sender_wallet_address(transaction.hash)
                    if not user_wallet in self.user.wallets_addresses:
                        self.user.wallets_addresses.append(user_wallet)
                        self.user.tokens += float(self._get_voter_balance(user_wallet))
                    self.user.save()
            if len(self.user.wallets_addresses) > user_wallets_count:
                return True
        return False

    def get_vote_answer(self, vote_title):
        answer_array = self.user.vote_data.get(vote_title)
        if answer_array:
            options = self.QUESTIONS.get(vote_title)
            try:
                return options[answer_array.index(1)]
            except ValueError:
                pass

    def get_question_answer(self, question_title):
        return self.user.extra_data.get(question_title)

    def vote(self):
        answers = {}
        answers.update(self.custom_answers)
        vote_data = self._map_vote_results(answers.copy())
        vote_data_weighted = self._map_vote_results(answers.copy(), weighted=True)
        self.user.vote_data = vote_data
        self.user.vote_data_weighted = vote_data_weighted
        self.user.has_voted = True
        self.user.extra_data = self.extra_data
        self.user.manifesto_version = MANIFESTO_VERSION
        self.user.save()

    @chatflow_step(title="Please fill in the following form", disable_previous=True)
    def custom_votes(self):
        """allow child classes to have its custom slides

        Returns:
            Dict, Dict: Has all questions and answer, extra saved data outside the poll
        """
        pass

    def _map_vote_results(self, form_answers, weighted=False):
        """takes form answers and returns a sparse array of what user chose
        to be easy in calcualting votes

        example: ["Blue", "Red", "Green", "Orange"]
        if user chose "Red" will [0, 1, 0, 0]
        if user chose "Red" and weighted results will [0, <user_token_sum>, 0, 0]
        Args:
            form_answers (dict): form result dictionary
        """
        for question, answer in form_answers.items():
            all_answers_init = len(self.QUESTIONS[question]) * [0.0]
            answer_index = self.QUESTIONS[question].index(answer)
            if weighted:
                all_answers_init[answer_index] = self.user.tokens
            else:
                all_answers_init[answer_index] = 1
            form_answers[question] = all_answers_init
        return form_answers

    @chatflow_step(title="Poll Results %", final_step=True)
    def result(self):
        usersnames = all_users.list_all()
        total_votes = 0
        total_answers = {}
        total_answers_weighted = {}
        for username in usersnames:
            user = all_users.get(username)
            if user.poll_name == self.poll_name and user.has_voted:
                total_votes += 1
                user_votes = all_users.get(username).vote_data
                user_votes_weighted = all_users.get(username).vote_data_weighted
                for question, answer in user_votes.items():
                    if total_answers.get(question):
                        total_answers[question] = list(map(sum, zip(total_answers[question], answer)))
                    else:
                        total_answers[question] = answer

                for question, answer in user_votes_weighted.items():
                    if total_answers_weighted.get(question):
                        total_answers_weighted[question] = list(map(sum, zip(total_answers_weighted[question], answer)))
                    else:
                        total_answers_weighted[question] = answer

        total_answers_with_percent = {k: self._calculate_percent(v) for k, v in total_answers.items()}
        total_answers_weighted_with_percent = {k: self._calculate_percent(v) for k, v in total_answers_weighted.items()}

        result_msg = ""
        for question, answers in total_answers_with_percent.items():
            question_current_title = question
            question_new_title = self.metadata["new_title_keys"][question_current_title]
            result_msg += f"### {question_new_title}\n"
            for i in range(len(answers)):
                answer_name = self.QUESTIONS[question][i]
                result_msg += f"- {answer_name}: {answers[i]}%\n"
            result_msg += "\n\n"

        # result_msg += "\n<br />\n\n"
        # result_msg += "## Weighted results %\n\n<br />\n\n"
        # for question, answers in total_answers_weighted_with_percent.items():
        #     question_current_title = question
        #     question_new_title = self.metadata["new_title_keys"][question_current_title]
        #     result_msg += f"### {question_new_title}\n"
        #     for i in range(len(answers)):
        #         answer_name = self.QUESTIONS[question][i]
        #         result_msg += f"- {answer_name}: {answers[i]}%\n"
        #     result_msg += "\n"

        result_msg += f"\n<br />\n\n#### Total number of votes: {total_votes}\n"
        self.md_show(result_msg, md=True)

    def _calculate_percent(self, answers):
        """Takes the answers list which is a sparse array and map it
        to percentages

        Args:
            answers (list)

        Returns:
            list: answers_list mapped to percentages
        """
        answers_list = answers[:]
        total_votes = float(sum(answers_list))
        for i in range(len(answers_list)):
            res = (answers_list[i] / total_votes) * 100
            answers_list[i] = round(res, 2)
        return answers_list

    def _get_voter_balance(self, wallet_address):
        """Get sum of user TFT and TFTA

        Args:
            wallet_address (String): Wallet address
        """
        assets = self.wallet.get_balance(wallet_address)
        total_balance = 0.0
        # get free balances
        for asset in assets.balances:
            if asset.asset_code == "TFT" or asset.asset_code == "TFTA":
                total_balance += float(asset.balance)

        # add locked funds too
        for locked_account in assets.escrow_accounts:
            for locked_asset in locked_account.balances:
                if locked_asset.asset_code == "TFT" or locked_asset.asset_code == "TFTA":
                    total_balance += float(locked_asset.balance)

        return total_balance
