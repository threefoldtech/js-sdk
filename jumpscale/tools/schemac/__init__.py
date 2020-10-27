'''
# schemac

Schemac is a tool used to convert (transpile) the schemas defined in jsx systems into the new objects definitions in js-ng

## Example

In this example there're bunch of types (bools, int, string, dict, time, date, enumerations, objects, list of objects, email) defined in jsx old style.

### jsx schema

```python
schema = """
@url = despiegk.test
listany = (LO)
llist2 = "" (LS) #L means = list, S=String
llist3     = [1,2,3] (LF)
today = (D)
now = (T)
info = (dict)
theemail = (email)
status = "on,off" (E)
happy = "yes, no" (E)
&nr    = 4
obj = (O)!hamada.test
lobjs = (LO) !hamada.test

date_start = 0 (I)
description* = "hello world"
description2 ** = 'a string' (S)
llist4*** = [1,2,3] (LI)
llist5 = [1,2,3] (LI)
llist6 = [1,2,3] (LI)
U = 0.0
nrdefault = 0
nrdefault2 = (I)
nrdefault3 = 0 (I)

@url = hamada.test
a = (I)
name = (S)
mood = "stressed,sleeping" (E)
"""
```

### Converting to the new system

We expect that to expand or convert to plain old python classes, with dependency resolution.



```python
    c = j.tools.schemac.get_compiler(schema, "python")
    assert c

    assert c._schema_text
    assert c.lang == "python"
    assert c.generator
    parsed_schemas = c.parse()  # parse schema now
    generated_python =c.generator.generate(parsed_schemas)
    print(generated_python)
```

### Generated file

```python
#GENERATED CLASS DONT EDIT
from jumpscale.core.base import Base, fields
from enum import Enum

class Status(Enum):
    On = 0
    Off = 1

class Happy(Enum):
    Yes = 0
    No = 1

class Mood(Enum):
    Stressed = 0
    Sleeping = 1



class HamadaTest(Base):
    a = fields.Integer()
    name = fields.String(default="")
    mood = fields.Enum(Mood)



class DespiegkTest(Base):
    listany = fields.List(fields.Object(Base))
    llist2 = fields.List(fields.String())
    llist3 = fields.List(fields.Float())
    today = fields.DateTime()
    now = fields.Time()
    info = fields.Typed(dict)
    theemail = fields.Email()
    status = fields.Enum(Status)
    happy = fields.Enum(Happy)
    nr = fields.String(default="4")
    obj = fields.Object(HamadaTest)
    lobjs = fields.List(fields.Object(HamadaTest))
    date_start = fields.Integer(default=0)
    description = fields.String(default="hello world")
    description2 = fields.String(default="a string")
    llist4 = fields.List(fields.Integer())
    llist5 = fields.List(fields.Integer())
    llist6 = fields.List(fields.Integer())
    U = fields.String(default="0.0")
    nrdefault = fields.String(default="0")
    nrdefault2 = fields.Integer()
    nrdefault3 = fields.Integer(default=0)

```
'''


def get_compiler(schema_text, lang="python"):
    from .compiler import Compiler

    return Compiler(lang, schema_text)
