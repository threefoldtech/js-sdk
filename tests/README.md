## How to run

### Unittests only

```bash
pytest . -sv -m "not integration"
```

### Integration tests only

```bash
pytest . -sv -m "integration"
```

### All tests

```bash
pytest . -sv
```
