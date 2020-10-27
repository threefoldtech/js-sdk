"""Generator based on JS-NG fields. takes in parsed schemas and generates Python classes based on JS-NG fields.

"""

from .plugin import Plugin

types_map = {
    "": "String",
    "S": "String",
    "O": "Object",
    "I": "Integer",
    "F": "Float",
    "B": "Boolean",
    "L": "List",
    "LS": "List",
    "LI": "List",
    "LF": "List",
    "LO": "List",
    "E": "Enum",
    "D": "DateTime",
    "T": "Date",
    "guid": "GUID",
    "email": "Email",
    "dict": "Object",
    "ipaddr": "IPAddress",
    "ipaddress": "IPAddress",
    "iprange": "IPRange",
    "json": "Json",
    "bytes": "Bytes",
    "I64": "Float",
}


def get_prop_line(prop):
    prop_type = prop.prop_type
    if prop_type == "B":
        if prop.defaultvalue.lower() == "true":
            prop.defaultvalue = "True"
        elif prop.defaultvalue.lower() == "false":
            prop.defaultvalue = "False"

    python_type = types_map.get(prop_type)
    line = f"{prop.name} = "
    # print(f"\n\n{prop.name} => {prop} \n\n")
    # primitive with a default or not.
    if prop_type == "E":
        line += f"fields.{python_type}({prop.name.capitalize()})"
    elif prop_type == "O":
        line += f"fields.{python_type}({prop.url_to_class_name})"
    elif prop_type == "LO" and prop.defaultvalue and prop.defaultvalue != "[]":
        line += f"fields.List(fields.Object({prop.url_to_class_name}))"
    elif prop_type == "LO" and not prop.defaultvalue:
        line += "fields.List(fields.Object(Base))"
    elif python_type == "L" and not prop.defaultvalue:
        line += " fields.List(fields.Object())"
    elif python_type == "L" and prop.defaultvalue:
        line += f" fields.List(fields.Object({prop.defaultvalue}))"
    elif len(prop_type) > 1 and prop_type[0] == "L":
        line += f"fields.List(fields.{types_map[prop_type[1:]]}())"
    elif prop_type in ["I", "F", "B"] and not prop.defaultvalue:
        line += f"fields.{python_type}()"
    elif prop_type in ["I", "F", "B"] and prop.defaultvalue:
        line += f"fields.{python_type}(default={prop.defaultvalue})"
    elif prop_type == "S":
        line += f'fields.String(default="{prop.defaultvalue}")'
    elif prop_type in ["T", "D"]:
        line += f"fields.{types_map[prop_type]}()"
    elif prop_type == "dict":
        line += "fields.Typed(dict)"
    elif prop_type in ["ipaddress", "ipaddr", "iprange"] and prop.defaultvalue:
        line += f'fields.{python_type}(default="{prop.defaultvalue}")'
    else:
        line += f"fields.{python_type}()"

    return line


SINGLE_TEMPLATE = """

class {{generated_class_name}}(Base):
{%- for prop in generated_properties.values() %}
    {{get_prop_line(prop)}}
{%- endfor %}

"""

TEMPLATE = """
#GENERATED CLASS DONT EDIT
from jumpscale.core.base import Base, fields
from enum import Enum

{%- for enum in enums %}

class {{enum['name']}}(Enum):
    {%- for enumval in enum['vals'] %}
    {{enumval}} = {{loop.index0}}
    {%- endfor %}
{%- endfor %}

{{classes_generated}}

"""


class JSNGGenerator(Plugin):
    def __init__(self):
        super().__init__()

        self._single_template = SINGLE_TEMPLATE
        self._template = TEMPLATE
        self._get_prop_line = get_prop_line
        self._types_map = types_map
