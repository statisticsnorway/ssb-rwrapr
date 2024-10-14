# Notes from converting to ssb-pypitemplate

This file describes the main changes when converting the repo to ssb-pypitemplate.

## Issues

- Renamed from `src/wrapr` to `srs/ssb_wrapr`, since `wrapr` already existed on testpypi.
- Format code with black and sort imports with isort.
- Move imports to the top of the modules. Having imports inside functions the modules
  are imported every time the function is called.
- Add devcontainer for working with code locally in vscode and PyCharm.
- Don't return from `finally` blocks, hides excpetions. Like this one:
  - src/wrapr/convert_py2r.py:111:17: B012 `return` inside `finally` blocks cause exceptions to be silenced
- Discuss error handling in `renv.py` and `function_wrapper.py`.
