"""The compiler that parses JSX schema and generates a suitable backend in a supported lanaguage.

"""

from jumpscale.loader import j
import re

from .plugins import CrystalGenerator, JSNGGenerator


ALLOWED_LANGS = {"python": JSNGGenerator, "jsng": JSNGGenerator, "crystal": CrystalGenerator}


def generator_by_name(language_name="python"):
    """Gets a generator by name

    Keyword Arguments:
        language_name (str) -- suitable generator (default: {"python"})

    Returns:
        (jumpscale.tools.schema.SchemaGenerator.Plugin) -- The generator to use. Default
    """
    return ALLOWED_LANGS[language_name]


class Compiler:
    def __init__(self, lang="python", schema_text=""):
        """Compiler class responsible for parsing schema_text and creating Parsed Schema objects with all metadata information needed.

        Keyword Arguments:
            lang (str)-- language to generate for (default: {"python"})
            schema_text (str)-- the schema text.
        """
        self._schema_text = schema_text
        self.lang = lang = lang
        self._parsed_schemas = {}

    @property
    def generator(self):
        """Gets generator by `self.lang`."""
        return generator_by_name(self.lang)()

    def parse(self):
        """Parses all the schemas in `self._schema_text` and returns Schema objects for generation"""
        schemas_texts = []
        to_process = self._schema_text
        if to_process.count("@url") == 1:
            schemas_texts = [self._schema_text]
        else:
            urls_positions = [m.start() for m in re.finditer("@url", self._schema_text)]
            urls_positions.append(len(self._schema_text))
            start_end_positions = list(zip(urls_positions, urls_positions[1:]))

            schemas_texts = [self._schema_text[start:end] for (start, end) in start_end_positions]

        parsed_schemas = [j.data.schema.parse_schema(schema_text) for schema_text in schemas_texts]
        self._parsed_schemas = {s.url_to_class_name: s for s in parsed_schemas}

        return self._parsed_schemas
