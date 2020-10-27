"""Generator for crystal language. Takes in parsed schemas and generates crystal language classes.
"""
from .plugin import Plugin
from jumpscale.loader import j

types_map = {
    "": "String",
    "S": "String",
    "O": "Object",
    "I": "Int64",
    "F": "Float",
    "B": "Boolean",
    "L": "[] of Object",
    "LS": "[] of String",
    "LI": "[] of Int64",
    "LF": "[] of Float",
    "LO": "",
}


def get_prop_line(prop):
    prop_type = prop.prop_type
    crystal_type = types_map.get(prop_type)
    line = f"property {prop.name}"

    # print(f"\n\n{prop.name} => {prop} \n\n")
    # primitive with a default or not.
    if prop_type == "E":
        line += f" : {prop.name.capitalize()}"
    elif prop_type == "O":
        line += f" : {prop.url_to_class_name}"
    elif prop_type == "LO" and prop.defaultvalue and prop.defaultvalue != "[]":
        line += f" : [] of {prop.url_to_class_name}"
    elif prop_type == "LO" and not prop.defaultvalue:
        line += f" : [] of Object"
    elif crystal_type == "L" and not prop.defaultvalue:
        line += f" : [] of Object"
    elif crystal_type == "L" and prop.defaultvalue:
        line += f" = {crystal_type}"
    elif len(prop_type) > 1 and prop_type[0] == "L" and prop_type[1] != "O":
        line += f" : {crystal_type}"

    elif prop_type in ["I", "F", "B"] and not prop.defaultvalue:
        line += f" : {crystal_type}"
    elif prop_type in ["I", "F", "B"] and prop.defaultvalue:
        line += f" = {prop.defaultvalue}"
    elif prop_type == "S":
        line += f' = "{prop.defaultvalue}"'
    else:
        line += f": {crystal_type}"

    return line


SINGLE_TEMPLATE = """

class {{generated_class_name}}
{%- for prop in generated_properties.values() %}
    {{get_prop_line(prop)}}
{%- endfor %}
end

"""

TEMPLATE = """
#GENERATED CLASS DONT EDIT

{%- for enum in enums %}

enum {{enum['name']}}:
    {%- for enumval in enum['vals'] %}
    {{enumval}} = {{loop.index0}}
    {%- endfor %}
end
{%- endfor %}


{{classes_generated}}

"""


class CrystalGenerator(Plugin):
    def __init__(self):
        super().__init__()

        self._single_template = SINGLE_TEMPLATE
        self._template = TEMPLATE
        self._get_prop_line = get_prop_line
        self._types_map = types_map
