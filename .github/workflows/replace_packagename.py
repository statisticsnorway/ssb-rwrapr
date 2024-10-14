"""This file adds a 'ssb-' prefix to the package name in pyproject.toml."""

from pathlib import Path

import tomlkit


toml_file = Path("pyproject.toml")
name = None

with toml_file.open(encoding="utf-8") as file:
    data = tomlkit.parse(file.read())

# Modify the value of [tool.poetry].name
if "tool" in data and "poetry" in data["tool"] and "name" in data["tool"]["poetry"]:
    name = data["tool"]["poetry"]["name"]
    data["tool"]["poetry"]["name"] = f"ssb-{name}"

# Add a [tool.poetry.packages] section to specify the name of the package directory,
# since it does not match the package name.
if name:
    data["tool"]["poetry"]["packages"] = [
        {"include": f"{name.replace('-', '_')}", "from": "src"},
    ]

with toml_file.open("w", encoding="utf-8") as file:
    tomlkit.dump(data, file)
