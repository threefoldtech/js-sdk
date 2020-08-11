.PHONY: tests docs

tests:
	pytest tests -sv

integrationtests:
	pytest tests -sv -m "integration"

unittests:
	pytest tests -sv -m "not integration"

docs:
	pdoc3 jumpscale --html --output-dir docs/api --overwrite
