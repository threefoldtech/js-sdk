from gevent import sleep
from jumpscale.loader import j


def retry(function):
    def wrapper(self, *args, **kwargs):
        for _ in range(6):
            try:
                result = function(self, *args, **kwargs)
                break
            except Exception as e:
                j.logger.warning(f"Failed to execute {function.__name__} due to error: {str(e)}")
                sleep(1)
        else:
            raise j.exceptions.Runtime(f"Failed to execute {function.__name__} after multiple retries")
        return result

    return wrapper
