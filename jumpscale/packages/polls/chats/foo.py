from jumpscale.sals.chatflows.polls import Poll


class Foo(Poll):
    poll_name = "foo"
    QUESTIONS = {
        "What's your favorite movie?": ["Avengers", "Lord of the rings", "Harry Potter", "something else"],
        "What's your favorite programing language?": ["Python", "Go", "Python bardo :P"],
        "Did you like the vote?": ["Yes", "No", "maybe"],
    }


chat = Foo
