from jumpscale.sals.chatflows.polls import Poll


class Example(Poll):
    poll_name = "example"
    QUESTIONS = {
        "What's your favorite color?": ["Blue", "Red", "Green", "Orange"],
        "What's your favorite Team?": ["Barcelona", "Manchester United", "AlAhly"],
        "Did you like the vote?": ["Yes", "No"],
    }

    def custom_votes(self):
        """allow to have custom slides
        just update custom_questions, custom_answers dicts
        extra_data: save data outside the poll

        Returns:
            Dict, Dict, Dict: Has all questions and choices, Has all questions and answer, extra saved
        """
        custom_questions = {}
        custom_answers = {}
        extra_data = {}

        q1 = "What's your favorite artist?"
        q1_choice = ["Amr Diab", "Adele", "Celin Dion", "Angham"]
        q1_answer = self.drop_down_choice(q1, q1_choice, required=True)
        custom_questions.update({q1: q1_choice})
        custom_answers.update({q1: q1_answer})

        feedback_text = "Please provide your feedback"
        feedback = self.text_ask(feedback_text)
        extra_data.update({"feedback": feedback})

        return custom_questions, custom_answers, extra_data


chat = Example
