## How to run

### Unittests only

```bash
pytest . -sv -m "unittests"
```

### Integration tests only

```bash
pytest . -sv -m "integration"
```

### All tests

```bash
pytest . -sv
```

### Generate tests docs from scratch

```bash
jsng "j.sals.testdocs.generate_tests_docs(source='tests/', target='docs/tests', clean=True)"
```

### Generate tests docs and append on the existing one

```bash
jsng "j.sals.testdocs.generate_tests_docs(source='tests/', target='docs/tests')"```
