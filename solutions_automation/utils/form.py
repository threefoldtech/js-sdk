def result(func):
    def wrapper(*args, **kwargs):
        res = Result()
        res.value = func(*args, **kwargs)
        return res

    return wrapper


class Result:
    def __init__(self):
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Form:
    def __init__(self, session):
        self._session = session
        self.fields = []
        self.results = []

    def ask(self, msg=None, **kwargs):
        pass

    def _append(self, msg, loader=str):
        self.fields.append(msg)
        result = Result(loader)
        self.results.append(result)
        return result

    @result
    def string_ask(self, msg, **kwargs):
        return self._session.string_ask(msg, **kwargs)

    @result
    def int_ask(self, msg, **kwargs):
        return self._session.int_ask(msg, **kwargs)

    @result
    def secret_ask(self, msg, **kwargs):
        return self._session.int_ask(msg, **kwargs)

    @result
    def datetime_picker(self, msg, **kwargs):
        return self._session.datetime_picker(msg, **kwargs)

    @result
    def multi_list_choice(self, msg, options, **kwargs):
        return self._session.multi_list_choice(msg, options, **kwargs)

    @result
    def upload_file(self, msg, **kwargs):
        return self._session.upload_file(msg, **kwargs)

    @result
    def multi_choice(self, msg, options, **kwargs):
        return self._session.multi_choice(msg, options, **kwargs)

    @result
    def single_choice(self, msg, options, **kwargs):
        return self._session.single_choice(msg, options, **kwargs)

    @result
    def drop_down_choice(self, msg, options, **kwargs):
        return self._session.drop_down_choice(msg, options, **kwargs)
