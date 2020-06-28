from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step


class Example(GedisChatBot):
    steps = [
        "step_1",
        "step_2",
        "step_3",
        "step_4",
        "step_5",
        "step_6",
        "step_7",
        "step_8",
        "step_9",
        "step_10",
        "step_11",
        "step_12",
        "step_13",
        "step_14",
        "step_15",
        "step_16",
        "step_17",
        "step_18",
    ]
    @chatflow_step(title="Step 1")
    def step_1(self):
        self.string_ask("String", required=True, min_length=5)
        self.loading_show("Please wait", 5)
        self.stop()
        self.string_ask("String 2")

    @chatflow_step(title="Step 2")
    def step_2(self):
        self.int_ask("Number (Minimum value is 5)", min=5)

    @chatflow_step(title="Step 3")
    def step_3(self):
        self.secret_ask("Password (Minimum length is 5)", min_length=5)

    @chatflow_step(title="Step 4")
    def step_4(self):
        self.text_ask("Text")

    @chatflow_step(title="Step 5")
    def step_5(self):
        self.datetime_picker("Date time")


chat = Example
