# IDE/Editor setup

## VSCode

[VSCode](https://code.visualstudio.com) is a very popular extensible code editor with many extensions to provide an IDE-like experience


### Poetry integration
You only need in `user settings` specify `python.venvPath` to the directory where poetry hosts its virtualenvs. e.g on linux that's `~/.cache/poetry/virtualenvs`

and make sure to select python interpreter (Ctrl+P then select interpreter)

### Recommended extensions

- `autoDocString` to ensure correct docstrings.
- `pyright` for static checking your code while writing in vscode.
- `AREPL` for a realtime python scratch pad.
- `Better TOML` toml config supported.
- `GitLens` for boosted git experience.
- `Git graph` view a graph of your repository.
- `Prettify JSON`
- `TabNine` AI based code completion
