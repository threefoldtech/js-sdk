from jumpscale.servers.gedis.baseactor import BaseActor, actor_method


class TestObject:
    def __init__(self):
        self.attr_1 = None
        self.attr_2 = None

    def to_dict(self):
        return self.__dict__

    def from_dict(self, ddict):
        self.__dict__ = ddict


class TestActor(BaseActor):
    @actor_method
    def add_two_numbers(self, x: int, y: int) -> int:
        """Adds two integers

        Arguments:
            x {int} -- first integer
            y {int} -- second integer

        Returns:
            int -- return the sum of the two integers
        """
        return x + y

    @actor_method
    def concate_two_strings(self, s1: str, s2: str) -> str:
        """Concates two strings

        Arguments:
            s1 {str} -- first string
            s2 {str} -- second string

        Returns:
            str -- {first string}{second string}
        """
        return s1 + s2

    @actor_method
    def update_object(self, obj: TestObject, data: dict) -> TestObject:
        """Update object

        Arguments:
            obj {TestObject} -- the object to be updated
            data {dict} -- new attributes values

        Returns:
            TestObject -- New object with the new data
        """
        obj.__dict__.update(**data)
        return obj

    @actor_method
    def update_objects(self, objs: list, data: list) -> list:
        """Update objects

        Arguments:
            objs {TestObject} -- list of objects to be updated
            data {dict} -- list of dicts contains the new data of the objects

        Returns:
            TestObject -- list of the new objects
        """
        for i, obj in enumerate(objs):
            obj.__dict__.update(**data[i])
        return objs


Actor = TestActor
