# Exception Handling

In Jumpscale all exceptions are caught by a global exception hook.


## Principles

- Do not overwrite sys.excepthook


## Add custom handler

You can register your own handler and set the minimum level of errors which the handler should handle.

```python
def my_error_handler(** error_dict):
    # Do something with the error dict

j.tools.errorhandler.register_handler(my_error_handler, level=40)
```

> The handler should expect the keywords argument of the [Error Dict](#error-dict)


## Intercept exception inside the code
```python
try:
    # something raises exception
except Exception as exception:
    j.tools.errorhandler.handle_exception(exception, level=40, die=False, stdout=True, category="custom_category")
```

- `level` : Level of the error, see [supported levels](#exceptions-levels)
- `die` : Set this flag to make program exit after handling the error.
- `stdout` : Set this flag to log the error.
- `category` : Set custom category (default: `exception`)


## Raising exceptions
We provide a carefully picked list of exceptions, you can find then [here](./exceptions.md)


## Error Dict

This an example of how the Error Dict looks like

```python
{
    "appname": "application name",
    "level":  "severity level",
    "message": "error message",
    "timestamp": "timestamp of the error",
    "category": "error category",
    "data": "optional dict to hold data",
    "traceback": {
        "raw": "traceback text",
        "process_id": "the process id"
        "stacktrace": [
            {
                "filename": "<file name>",
                "filepath": "<file path>",
                "context": "<function name>",
                "linenr": "<line number>",
                "code": "<line code>"
            }
        ]
},
```

## Exceptions levels

- `CRITICAL` 	50
- `ERROR` 	40
- `WARNING`	30
- `INFO `	    20
- `STDOUT` 	15
- `DEBUG` 	10
