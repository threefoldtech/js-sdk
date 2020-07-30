from jumpscale.loader import j


class TemporaryProblem(j.exceptions.JSException):

    def __init__(self, message):
        self.message=message
        super().__init__(self, message)

    def __str__(self):
        return self.message

class NoTrustLine(j.exceptions.JSException):
    def __init__(self):
        super().__init__(self, "Receiver has no trustline")

    def __str__(self):
        return "Receiver has no trustline"

class TooLate(TemporaryProblem):
    def __init__(self):
        super().__init__(self, "The transaction failed to be submitted to the network in time")
