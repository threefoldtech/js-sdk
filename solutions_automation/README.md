# Automated solutions deployment

## Make a new automation class

To make a new automated deployment class, create a new class that inherits from `GedisChatBotPatch` in _gedispatch.py_.

This base class is augmented with questions present in all marketplace apps to avoid repeating them for every app.

In case of admin solution automation, the messages are not the same so you must enter them by hand in the new class. The messages and their answers should be defined in the class variable QS as follows:

```python
QS = {
MESSAGE: "result"
}
```

The `MESSAGE` should be a string or a regular expression. Whenever the chatbot asks a question, whether it's for an integer, a string, or a choice, the response to it is calculated from the result string. `result` could be a variable or a method. In case of being a variable, its value is returned. For the method case. The method is called with the arguments passed by the chat bot (this could be useful in case of `single_choice` questions whose options is not defined before the chat start). The method `choose_random` is provided in `GedisChatBotPatch` to choose a random choice for single_choice and drop down queries.

The variables that is present in the `QS` dict must be present as an argument when creating a new instance of the child class.

Basic questions are added in the base class so you don't have to add them (solution_name, currency, expiration).

For example,

```python

class AutomatedNewApp(GedisChatBotPatch):
    QS = {
        "How old are you?": "age",
        "Choose you favorite color?": "choose_color"
    }

    def choose_color(self, msg, options, *args, **kwargs):
        return options[0]

deployed_new_app = AutomatedNewApp(age=11, debug=True)
```

Just initializing the class begins the work. The debug option specifies whether the `md_show` should print or suppress the message.

## Use an existing one

Inside `deployer.py`, there're methods to deploy the solutions with the parameters specified in them with the default values.

Another way is to import the class and instantiate a new object as follows:

```python
from ubuntu import UbuntuAutomated

test = UbuntuAutomated(
    solution_name="ubnutu",
    currency="TFT",
    version="ubuntu-18.04",
    cpu=1,
    memory=1024,
    disk_size=256,
    disk_type="SSD",
    log="NO",
    ssh="~/.ssh/id_rsa.pub",
    ipv6="NO",
    node_automatic="NO",
    debug=True,
)
```
