from jumpscale.loader import j

class Temporaryproblem(j.exceptions.JSException):
    def __init__(self, message):
        super().__init__(self, message)