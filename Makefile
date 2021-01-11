.PHONY: tests docs api_docs docs-serve

tests:
	pytest tests -sv

testdocs:
	jsng "j.sals.testdocs.generate_tests_docs(source='tests/', target='docs/tests', clean=True)"

integrationtests:
	pytest tests -sv -m "integration"

unittests:
	pytest tests -sv -m "unittests"

api_docs:
	pdoc3 jumpscale --html --output-dir docs/api --force

docs: api_docs

docs-serve:
	python3 -m http.server --directory ./docs

requirements.txt:
	 poetry lock && poetry run pip freeze > $@
