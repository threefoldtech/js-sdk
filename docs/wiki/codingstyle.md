# Coding and Documentation style guide


## Code
We stress on clean code based on pep8 and more strict checks [wemake](https://wemake-python-stylegui.de/en/latest/index.html)


### General
- Use only ASCII characters for names
- Do not use transliteration from any other languages, translate names instead
- Use clear names, do not use words that do not mean anything like obj
- Use names of an appropriate length: not too short, not too long
- Do not mask builtins
- Do not use unreadable charachter sequences like O0 and Il
- Protected members should use underscore as the first char
- Private names with two leading underscores are not allowed
- If you need to explicitly state that the variable is unused, prefix it with _ or just use _ as a name
- Do not use variables that are stated to be unused, rename them when actually using them
- Do not define unused variables unless you are unpacking other values as well
- Do not use multiple underscores (__) to create unused variables
- Whenever you want to name your variable similar to a keyword or builtin, use trailing _
- Do not use consecutive underscores
- When writing abbreviations in UpperCase capitalize all letters: HTTPAddress
- When writing abbreviations in snake_case use lowercase: http_address
- When writing numbers in snake_case do not use extra _ before numbers as in http2_protocol


### Packages
Packages must use snake_case
One word for a package is the most preferable name

### Modules
- Modules must use snake_case
- Module names must not overuse magic names
- Module names must be valid Python identifiers

### Classes
- Classes must use UpperCase
- Python’s built-in classes, however, are typically lowercase words
- Exception classes must end with Error

### Instance attributes
- Instance attributes must use snake_case with no exceptions

### Class attributes
- Class attributes must use snake_case with no exceptions
- Enum fields also must use snake_case

### Functions and methods
- Functions and methods must use snake_case with no exceptions

### Method and function arguments
- Instance methods must have their first argument named self
- Class methods must have their first argument named cls
- Metaclass methods must have their first argument named mcs
- Python’s *args and **kwargs should be default names when just passing these values to some other - method/function, unless you want to use these values in place, then name them explicitly

### Global (module level) variables
- Global variables must use CONSTANT_CASE
- Unless other is required by the API, example: urlpatterns in Django

### Variables
- Variables must use snake_case with no exceptions
- When a variable is unused it must be prefixed with an underscore: _user

### Type aliases

- Must use UpperCase as real classes
- Must not contain word type in its name
- Generic types should be called clearly and properly, not just TT or KT or VT

... more to be added for coding style.

## Documentation

### Module
- Every module starts with a docstring describing the module and its purpose and a little snippet of code of some of its use cases. check [fields](https://github.com/threefoldtech/js-ng/blob/44b5b99373c3ef677aae721324ba5e8d5a042f80/jumpscale/core/base/fields.py#L1) module for inspiration
- Markdown is valid in the docstrings so you can make use of anything markdown.
- When you want to reference something in the rest of your module use backticks around the identifier
- If you want to reference with a fully qualified name write it in the docstring surrounded with backticks e.g `jumpscale.core.base.meta`.


### Class

For classes add the docstring in the `__init__`

```python
class Field:
    def __init__(self, default=None, required=False, indexed=False, readonly=False, validators=None, **kwargs):
        """
        Base field for all field types, have some common options that can be used any other field type too.


        Args:
            default (any, optional): default value. Defaults to None.
            required (bool, optional): required or not. Defaults to False.
            indexed (bool, optional): indexed or not. Defaults to False.
            readonly (bool, optional): can only get the value. Defaults to False.
            validators (list of function, optional): a list of functions that takes a value and raises ValidationError if not valid. Defaults to None.
        """
```

### Method or Function

```python
    def validate(self, value):
        """
        validate value if required and call custom self.validators if any

        Args:
            value (any): in case value is not valid

        Raises:
            ValidationError: [description]
        """
```

