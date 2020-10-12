from gevent import monkey

monkey.patch_all(subprocess=False)

from jumpscale.loader import j

tests_docs_locations = []


def pytest_collection_modifyitems(items, config):
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker("unittests")


def pytest_addoption(parser):
    parser.addoption("--generate-docs", action="store_true", help="Generate docs for the running tests in `docs/tests`")
    parser.addoption(
        "--docs-from-scratch",
        action="store_true",
        help="Remove tests docs before starting running the tests, this only works with --generate-docs",
    )


def pytest_sessionstart(session):
    if session.config.option.docs_from_scratch and session.config.option.generate_docs:
        doc_location = j.sals.fs.join_paths(j.sals.fs.parent(__file__), "../docs/tests")
        j.sals.fs.rmtree(doc_location)


def pytest_runtest_setup(item):
    args = item.config.args
    if item.config.option.generate_docs and not check_running_only_test(args):
        generate_docs(item)


def generate_docs(item):
    doc = item._obj.__doc__
    name = item.name
    if doc:
        # Format the docs.
        doc = doc.replace("  ", "")
        test_doc = f"### {name}\n\n{doc}"
        test_doc = test_doc.replace("**Test Scenario**", "**Test Scenario**\n")

        # Get target docs locations.
        doc_location = j.sals.fs.join_paths(j.sals.fs.parent(__file__), "../docs")
        test_location = item.location[0].replace(".py", ".md")
        target_location = j.sals.fs.join_paths(doc_location, test_location)

        # Check if the docs exists and remove them in this case to generate a new one.
        if target_location not in tests_docs_locations:
            tests_docs_locations.append(target_location)
            if j.sals.fs.exists(target_location):
                j.sals.fs.rmtree(target_location)

        # Write docs.
        j.sals.fs.mkdirs(j.sals.fs.parent(target_location))
        if j.sals.fs.exists(target_location):
            with open(target_location, "a") as f:
                f.write("\n")
                f.write(test_doc)
        else:
            j.sals.fs.write_file(target_location, test_doc)

        # add entry to main README.md
        category = item.location[0].split(j.sals.fs.sep)[1].capitalize()
        file_name = item.location[0].split(j.sals.fs.sep)[-1].replace(".py", "")
        relative_location = test_location.replace("tests/", "", 1)
        add_entry_to_main_readme(category, file_name, relative_location)

    else:
        j.logger.warning(f"Test {name} doesn't have docstring")


def check_running_only_test(args):
    for arg in args:
        if "::" in arg:
            return True
    return False


def add_entry_to_main_readme(category, file_name, relative_location):
    readme_location = j.sals.fs.join_paths(j.sals.fs.parent(__file__), "../docs/tests/README.md")
    readme = ""
    if j.sals.fs.exists(readme_location):
        readme = j.sals.fs.read_file(readme_location)
    category = f"### {category}\n\n"
    new_entry = f"- [{file_name}]({relative_location})\n"
    if not new_entry in readme:
        if not category in readme:
            new_line = "\n" if readme else ""  # For the first line in README.
            readme = f"{readme}{new_line}{category}"

        # Get the last line in the category.
        last_line = readme.find("###", readme.find(category) + len(category)) - 1
        if last_line > 0:
            new_readme = f"{readme[:last_line]}{new_entry}{readme[last_line:]}"
        else:
            new_readme = f"{readme}{new_entry}"
        j.sals.fs.rmtree(readme_location)
        j.sals.fs.write_file(readme_location, new_readme)
