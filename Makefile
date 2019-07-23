.PHONY: tests docs

tests:
	pytest tests

docs:
	pdoc3 jumpscale --html --output-dir docs/api --overwrite