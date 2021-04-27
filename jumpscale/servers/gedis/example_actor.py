from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from typing import Sequence
from jumpscale.loader import j
import inspect, sys


class TestObject:
    def __init__(self):
        self.attr = None

    def to_dict(self):
        return self.__dict__

    def from_dict(self, ddict):
        self.__dict__ = ddict


class Example(BaseActor):
    @actor_method
    def add_two_ints(self, x: int, y: int) -> int:
        """Adds two ints

        Arguments:
            x {int} -- first int
            y {int} -- second int

        Returns:
            int -- the sum of the two ints
        """
        return x + y

    @actor_method
    def concate_two_strings(self, x: str, y: str) -> str:
        """Concate two strings

        Arguments:
            x {str} -- first string
            y {str} -- second string

        Returns:
            str -- the concate of the two strings
        """
        return x + y

    @actor_method
    def modify_object(self, myobj: list, new_value: int) -> list:
        """Modify atrribute attr of the given object

        Arguments:
            myobj {TestObject} -- the object to be modified

        Returns:
            TestObject -- modified object
        """
        for i in range(len(myobj)):
            myobj[i].attr = new_value * (i + 1)
        return myobj


Actor = Example
