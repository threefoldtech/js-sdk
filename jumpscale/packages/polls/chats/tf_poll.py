from jumpscale.sals.chatflows.polls import Poll
from textwrap import dedent


VOTES = {
    1: {
        "title": "Reading June 2020 update document",
        "content": "### It's very important that you as a ThreeFold token holder (TFTA) have read our latest update document on https://wiki.threefold.io/#/threefold_update_june2020.md",
        "options": [
            "I have read the June 2020 update document",
            "I have not read the June 2020 update document"
        ]
    },
    2: {
        "title": "Reading the manifesto",
        "content": "### It's very important that you as a ThreeFold token holder (TFTA) have read and agree with the decentralization manifesto of our TFGrid. This manifesto is the basis of our further evolution and needs to be accepted by all of us.",
        "options": [
            "I have read the manifesto and I do agree.",
            "I have not read the manifesto or I do not agree."
        ]
    },
    3: {
        "title": "TFTA on Stellar rights",
        "content": dedent("""\
        TFTA on Stellar has all the same rights and more compared to the TFT on Rivine

        I can

        - Buy any capacity on the TF Grid, which represents the main use-case of this token.
        - SellTFTA to anyone (directly or using Stellar Exchange or using atomic swaps).
        - Transfer TFTA to anyone.
        - Enjoy any other feature you would expect from a digital currency.

        No rights have been taken away from me by switching blockchains.

        """),
        "options": [
            "I do agree",
            "I do not agree"
        ]
    },
    4: {
        "title": "test",
        "content": "### The following vote is incredibly important, do realize that if we bring the TFTA on the public exchanges without price protection that there is a big probability that the price will drop way below USD 0.15. The TF Foundation believes that by growing our demand organically and executing the steps as outlined in our update document the token will get liquidity in a stable and organic way. Please keep in mind that the token is only 2 years and 2 months old. If there is no price protection we will have no choice than to stop with the TDE which means the TF Foundation will have no funding to continue and the planned promotion activities will stop. This will also mean that we will not go for the option of using onboarding tokens & partnerships like Dash & DigiByte which would allow us to go 100% decentralized for exchanging TFT to any of these onboarding tokens.",
        "options": [
            "I am fine with the option to sell my TFTA (TFTv1) on the Stellar exchange or any other decentralized market mechanism and get automatic conversion to TFTv2 end of the year.",
            "I want my TFTA to be available on supported exchanges as TFT and agree with minimal price protection (0.15 USD, +2% increase per month starting with May 1), sales will happen through a sales bot.",
            "I want my TFTA to be available on the 3 supported exchanges as TFT and there should be no price protection. I do realize this choice has the potential to damage the ThreeFold movement."
        ]
    }
}


class TFPoll(Poll):
    poll_name = "tf_poll"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.QUESTIONS = {}
        self.extra_data = {}
        self.custom_answers = {}


    def welcome(self):
        
        statement_1 = """\
        Dear ThreeFold Token Holder, 

        This is the first poll organized by the foundation using our newly developed ThreeFold voting system. Your votes at the end of this wizard are super important to the future of the ThreeFold Grid (TF Grid). 
        This poll is only for TFT v1 holders (TFTA).

        This first poll is related to introducing a new era in the ThreeFold Grid which leads to even more decentralization and it is important to have your support.
        To understand the why and how of this poll consult: https://wiki.threefold.io/#/decentr
        The detailed poll results will only be visible & consulted by the members of the TFgrid Council: see https://wiki.threefold.io/#/threefold_councils.md
        Only the end results will be visible by the general community which is

        - The voting questions (comes at end of this poll)
        - % of votes as results per question, weighted and unweighted
        - Unweighted means: each vote = 1, weighted means each vote in relation to nr of tokens the vote represents.

        INSERT: GDPR disclaimer (see Pierre)
        """
        
        self.md_show(dedent(statement_1), md=True)

        full_name = self.string_ask("What is your full name ?", required=True)
        self.extra_data.update({"full_name": full_name})

        statement_2 = """\
        ### Please read the introduction to this poll on link: https://wiki.threefold.io/#/threefold_poll_2_1.md
        
        ### Please read the decentralization manifesto on http://decentralization2.threefold.io  (doc not there yet now on: https://docs.google.com/document/d/1IASWZWC7N-l_JVyKpjmzrbitXjQh9wUjQxuflEzTYck/edit#)
        """

        self.md_show(dedent(statement_2), md=True)

        question_1 = """\
        ### Mark all which is relevant how you got your tokens

        ### This is confidential information and is only visible to the TFGrid Council.
        """

        question_1_choices = {
            "My TFT as the result of farming IT capacity": "Result of farming IT capacity",
            "I bought TFT from the market, which means through atomic swap, a public exchange or from any other TFT holder": "From Market",
            "I bought my TFT from Mazraa (ThreeFold FZC) = part of TF Foundation": "From Mazraa",
            "I bought my TFT from BetterToken = part of TF Foundation": "From BetterToken",
            "Gift from TF Foundation": "From Gifts"
        }

        question_1_answer = self.multi_choice(dedent(question_1), options=list(question_1_choices.keys()), md=True, required=True)
        self.extra_data.update({"question_1": question_1_answer})

        form = self.new_form()

        percentages = []
        for answer in question_1_answer:
            percentages.append(form.int_ask(question_1_choices[answer]))
            
        form.ask("### For every selected option above let us please now the percentage of your total amount of  TFT (if more than 1 option)")
        self.extra_data.update({"question_2": [v.value for v in percentages]})

    def custom_votes(self):
        super().custom_votes()

        vote_1_answer = self.single_choice(VOTES[1]["content"].strip(), VOTES[1]["options"], md=True, required=True)
        self.QUESTIONS.update({VOTES[1]["title"]: VOTES[1]["options"]})
        self.custom_answers.update({VOTES[1]["title"]: vote_1_answer})

        vote_2_answer = self.single_choice(VOTES[2]["content"].strip(), VOTES[2]["options"], md=True, required=True)
        self.QUESTIONS.update({VOTES[2]["title"]: VOTES[2]["options"]})
        self.custom_answers.update({VOTES[2]["title"]: vote_2_answer})

        if vote_1_answer == VOTES[1]["options"][1] or vote_2_answer == VOTES[2]["options"][1]:
            self.stop("Thank you for your participation, The poll ends now because you did read the June 2020 update document and/or did not read the manifesto.")
        else: 
            self.md_show("Thank you for confirming our \"decentralization manifesto\", you have now digitally signed this document.")

        vote_3_answer = self.single_choice(VOTES[3]["content"].strip(), VOTES[3]["options"], md=True, required=True)
        self.QUESTIONS.update({VOTES[3]["title"]: VOTES[3]["options"]})
        self.custom_answers.update({VOTES[3]["title"]: vote_3_answer})

        vote_4_answer = self.single_choice(VOTES[4]["content"].strip(), VOTES[4]["options"], md=True, required=True)
        self.QUESTIONS.update({VOTES[4]["title"]: VOTES[4]["options"]})
        self.custom_answers.update({VOTES[4]["title"]: vote_4_answer})

        self.vote()


chat = TFPoll
