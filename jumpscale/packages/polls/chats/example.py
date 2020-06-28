from jumpscale.sals.chatflows.polls import Poll


class Example(Poll):
    poll_name = "example"
    QUESTIONS = {
        "What's your favorite color?": ["Blue", "Red", "Green", "Orange"],
        "What's your favorite Team?": ["Barcelona", "Manchester United", "AlAhly"],
        "Did you like the vote?": ["Yes", "No"],
    }


chat = Example
