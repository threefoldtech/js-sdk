from jumpscale.loader import j


class TemporaryProblem(j.exceptions.JSException):
    def __init__(self, message):
        super().__init__(self, message)
