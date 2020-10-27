from unittest import skip

from hypothesis import given
from hypothesis.strategies import integers, lists
from jumpscale.loader import j

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


valid_generated_python = """
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

"""

valid_generated_crystal = """
#GENERATED CLASS DONT EDIT

enum Status:
    On = 0
    Off = 1
end

enum Happy:
    Yes = 0
    No = 1
end

enum Mood:
    Stressed = 0
    Sleeping = 1
end




class HamadaTest
    property a : Int64
    property name = ""
    property mood : Mood
end




class DespiegkTest
    property listany : [] of Object
    property llist2 : [] of String
    property llist3 : [] of Float
    property status : Status
    property happy : Happy
    property nr = "4"
    property obj : HamadaTest
    property lobjs : [] of HamadaTest
    property date_start = 0
    property description = "hello world"
    property description2 = "a string"
    property llist4 : [] of Int64
    property llist5 : [] of Int64
    property llist6 : [] of Int64
    property U = "0.0"
    property nrdefault = "0"
    property nrdefault2 : Int64
    property nrdefault3 = 0
end

"""


@skip("https://github.com/threefoldtech/js-ng/issues/422")
def test001_loading_schema_in_compiler():
    c = j.tools.schemac.get_compiler(schema, "python")
    assert c

    assert c._schema_text
    assert c.lang == "python"
    assert c.generator
    parsed_schemas = c.parse()  # parse schema now
    generated_python = c.generator.generate(parsed_schemas)
    print(generated_python)

    for line in valid_generated_python.splitlines():
        if line.strip():
            assert line in generated_python


# Disabled for now.
# def test002_loading_schema_and_convert_to_crystal():
#     c = j.tools.schemac.get_compiler(schema, "crystal")
#     assert c

#     assert c._schema_text
#     parsed_schemas =c.parse()
#     generated_crystal = c.generator.generate(parsed_schemas)
#     print(generated_crystal)
#     for line in valid_generated_crystal.splitlines():
#         if line.strip():
#             assert line in generated_crystal
