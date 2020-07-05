from jumpscale.sals.chatflows.polls import Poll


class New(Poll):
    poll_name = "new"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.QUESTIONS = {
            "What's your favorite color?": ["Blue", "Red", "Green", "Orange"],
            "What's your favorite Team?": ["Barcelona", "Manchester United", "AlAhly"],
            "Did you like the vote?": ["Yes", "No"],
        }

    def welcome(self):
        statement_1 = """
        Dear ThreeFold Token Holder, 

        This is the first poll organized by the foundation using our newly developed ThreeFold voting system. Your votes at the end of this wizard are super important to the future of the ThreeFold Grid (TF Grid). 
        This poll is only for TFT v1 holders (TFTA).

        This first poll is related to introducing a new era in the ThreeFold Grid which leads to even more decentralization and it is important to have your support.

        To understand the why and how of this poll consult: https://wiki.threefold.io/#/decentr

        The detailed poll results will only be visible & consulted by the members of the TFgrid Council: see https://wiki.threefold.io/#/threefold_councils.md

        Only the end results will be visible by the general community which is

        - the voting questions (comes at end of this poll)
        - % of votes as results per question, weighted and unweighted
        - unweighted means: each vote = 1, weighted means each vote in relation to nr of tokens the vote represents.

        INSERT: GDPR disclaimer (see Pierre)

        ## Get to know voting rights email addr, ...

        - ask for more than 1 TFTA (there can be more than 1 wallet linked to the vote)
        - keep on asking is this your email address and the amount of TFT you want to vote with
        - result needs to be that user agreed that this is his email address, 3bot name and the TFT linked to the poll are ok
        - every time the user comes back to this poll we have to show this again and ask if correct, if not allow correction
        """
        
        self.md_show(statement_1, md=True)

        statement_2 = """
        Please read the introduction to this poll on link: https://wiki.threefold.io/#/threefold_poll_2_1.md
        Please read the decentralization manifesto on http://decentralization2.threefold.io  (doc not there yet now on: https://docs.google.com/document/d/1IASWZWC7N-l_JVyKpjmzrbitXjQh9wUjQxuflEzTYck/edit#)
        """
        x = self.multi_choice("aaaaaaaaaa", ["a", "b", "c"])
        self.md_show(str(x), md=True)




    # def custom_votes(self):
    #     """allow to have custom slides
    #     just update custom_questions, custom_answers dicts
    #     extra_data: save data outside the poll

    #     Returns:
    #         Dict, Dict: Has all questions and answer, extra saved
    #     """
    #     custom_answers = {}
    #     extra_data = {}

    #     q1 = "What's your favorite artist?"
    #     q1_choice = ["Amr Diab", "Adele", "Celin Dion", "Angham"]
    #     q1_answer = self.drop_down_choice(q1, q1_choice, required=True)
    #     self.QUESTIONS.update({q1: q1_choice})
    #     custom_answers.update({q1: q1_answer})

    #     feedback_text = "Please provide your feedback"
    #     feedback = self.text_ask(feedback_text)
    #     extra_data.update({"feedback": feedback})

    #     return custom_answers, extra_data


chat = New
