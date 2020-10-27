from jumpscale.loader import j


class Plugin:
    def _generate_single(self, schema):
        """Generates a single schema template

        Arguments:
            schema (jumpscale.data.Schema) -- Parsed schema.

        Returns:
            (str) -- schema convert to a class as string.
        """
        data = dict(
            generated_class_name=schema.url_to_class_name,
            generated_properties=schema.props,
            types_map=self._types_map,
            enums=schema.get_enums_required(),
            classes=schema.get_classes_required(),
            get_prop_line=self._get_prop_line,
        )
        return j.tools.jinja2.render_template(template_text=self._single_template, **data)

    def generate(self, parsed_schemas):
        """Generates a string has all the enumerations and classes in the target language.

        Arguments:
            parsed_schemas (Dict[str, jumpscale.data.Schema]) -- a dict of schema name to schema object

        Returns:
            (str) -- Compiled string of all enumerations and classes in the target language.
        """
        all_enums = []
        for scm_name, scm in parsed_schemas.items():
            enums = scm.get_enums_required()
            for enum in enums:
                if enum not in all_enums:
                    all_enums.append(enum)

        depsresolver = j.tools.depsresolver
        all_classes = []
        for scm_name, scm in parsed_schemas.items():
            depsresolver.add_task(scm.url_to_class_name, scm.get_classes_required(), lambda x: x)

        independent_schemas = [name for name, deps in depsresolver.tasksgraph.items() if not deps]
        for schema_name in independent_schemas:
            all_classes.append(self._generate_single(parsed_schemas[schema_name]))

        dependant_schemas = [name for name, deps in depsresolver.tasksgraph.items() if deps]
        for schema_name in dependant_schemas:
            all_classes.append(self._generate_single(parsed_schemas[schema_name]))

        all_classes_str = "\n\n".join(all_classes)
        return j.tools.jinja2.render_template(
            template_text=self._template, classes_generated=all_classes_str, enums=all_enums
        )
