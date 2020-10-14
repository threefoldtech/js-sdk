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
pytest tests -sv --generate-docs --docs-from-scratch
```

### Generate tests docs and append on the existing one

```bash
pytest tests -sv --generate-docs
```
