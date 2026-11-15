"""Structural diff between two TOML documents.

Compares two TOML texts key-path by key-path and reports which keys were
added, removed, or had their values changed. Keys are reported as dotted
paths (e.g. ``db.port``); array-of-table elements are indexed
(e.g. ``items.0.name``).
"""

from __future__ import annotations

from typing import Any, Dict, List, NamedTuple

from tomlkit.api import parse
from tomlkit.container import Container
from tomlkit.items import AbstractTable, AoT, Item


class TomlDiff(NamedTuple):
    """Result of :func:`diff_toml`.

    Attributes are lists of dotted key paths, in document order.
    """

    added: List[str]
    removed: List[str]
    changed: List[str]


def _flatten(node: Any, prefix: str, out: Dict[str, Any]) -> None:
    """Flatten a table/container into ``{dotted_path: unwrapped_value}``.

    Tables (including inline tables) are recursed into; arrays of tables are
    recursed into with the element index appended to the path; everything
    else is a leaf value.
    """
    if isinstance(node, (Container, AbstractTable)):
        items = node.items()
    elif isinstance(node, dict):
        items = node.items()
    else:
        return

    for key, value in items:
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, (Container, AbstractTable)):
            _flatten(value, path, out)
        elif isinstance(value, AoT):
            for i, element in enumerate(value):
                _flatten(element, f"{path}.{i}", out)
        elif isinstance(value, Item):
            out[path] = value.unwrap()
        else:
            out[path] = value


def diff_toml(old_text: str, new_text: str) -> TomlDiff:
    """Diff two TOML documents and return key-path level changes.

    :param old_text: the original TOML document
    :param new_text: the updated TOML document
    :return: a :class:`TomlDiff` with ``added``, ``removed`` and ``changed``
        lists of dotted key paths.
    """
    old_flat: Dict[str, Any] = {}
    new_flat: Dict[str, Any] = {}
    _flatten(parse(old_text), "", old_flat)
    _flatten(parse(new_text), "", new_flat)

    added = [path for path in new_flat if path not in old_flat]
    removed = [path for path in old_flat if path not in new_flat]
    changed = [
        path
        for path in old_flat
        if path in new_flat and old_flat[path] != new_flat[path]
    ]

    return TomlDiff(added=added, removed=removed, changed=changed)
